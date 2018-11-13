#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import importlib
import logging
import warnings
import os
import subprocess
import sys
import time
import shutil
import argparse

import jobs
from jobs import tools


default_jobs = {
    tools.Target.COSMO: ["meteo", "icbc", "emissions", "biofluxes", "int2lm",
                         "post_int2lm", "cosmo", "post_cosmo"],
    tools.Target.COSMOART: ["meteo", "icbc", "emissions", "obs_nudging",
                            "photo_rate", "int2lm", "cosmo", "post_cosmo"]
}


def parse_arguments():
    """Parse the command line arguments given to this script
    
    Returns
    -------
    Namespace-object
    """
    parser = argparse.ArgumentParser(description="Run the processing chain.")

    parser.add_argument("casenames",
                        nargs='+',
                        help="List of identifiers for the runs. "
                        "The config-files for each run is assumed "
                        "to be in cases/<casename>/. The runs are executed "
                        "sequentially in the order they're given here.")

    times_help = ("Triplet of {date hstart hstop} | "
                  "date: Startdate of the run in the format "
                  "yyyy-mm-dd | "
                  "hstart: Time on the startdate when the "
                  "simulation starts. If this is zero, the "
                  "simulation starts at midnight of the +startdate. | "
                  "hstop: Length of the simulation in hours. The "
                  "simulation runs until startdate + hstart + "
                  "hstop. Depending on your config.py settings, "
                  "processing-chain will split up the simulation "
                  "and perform several restarts before reaching the "
                  "stopping-time.")
    parser.add_argument("times",
                        nargs=3,
                        help=times_help)

    jobs_help = ("List of job-names to be executed. A job is a .py-"
                 "file in jobs/ with a main()-function which "
                 "handles one aspect of the processing chain, for "
                 "example copying meteo-input data or launching a "
                 "job for int2lm. "
                 "Jobs are executed in the order in which they are "
                 "given here. "
                 "If no jobs are given, the default that will be "
                 "executed is: COSMO: {} | COSMOART : {}"
                 .format(default_jobs[tools.Target.COSMO],
                         default_jobs[tools.Target.COSMOART]))
    parser.add_argument("-j", "--jobs",
                        nargs='*',
                        dest="job_list",
                        help=jobs_help,
                        default=None)
    
    args = parser.parse_args()
    args.startdate = args.times[0]
    args.hstart = int(args.times[1])
    args.hstop = int(args.times[2])
    return args

def load_config_file(casename, cfg):
    """Load the config file.
    
    Looks for the config file in ``cases/casename/config.py`` and then imports
    it as a module. This lets the config file contain python statements which
    are evaluated on import.

    If this is not the first config-file to be imported by run_chain.py, the
    module has to be reloaded to overwrite the values of the old case.

    Access variables declared in the config-file (``myval = 9``) with
    ``cfg.myval``.

    Add new variables with::
    
        setattr(cfg, 'myval', 9)
        
    Parameters
    ----------
    casename : str
        Name of the folder in cases/ where the configuration files are stored
    cfg : module or None
        If cfg is None, the module is freshly imported. If it is a module
        object, that module is reloaded.
        
    Returns
    -------
    config-object
        Object with all variables as attributes
    """
    try:
        fn = os.path.join('cases',casename,'config')
        sys.path.append(os.path.dirname(fn))

        if cfg is None:
            cfg = importlib.import_module(os.path.basename(fn))
        else:
            cfg = importlib.reload(cfg)

        # so that a different cfg-file can be imported later
        sys.path.pop()
    except IndexError:
        print('ERROR: no config file provided!')
        sys.exit(1)
    except ImportError:
        print('ERROR: failed to import config module "%s"!' % fn)
        sys.exit(1)

    return cfg


def set_simulation_type(cfg):
    """Detect if the chain targets cosmo or cosmoart
    
    Check if a target was provided in the config-object. If no target is 
    provided, set the target to cosmo in the config-object.

    Raise a RuntimeError if a unsupported target is given in cfg.

    Translates the target from string to enum.

    Parameters
    ----------
    cfg : config-object
    """
    default = 'cosmo'

    target_str = getattr(cfg, 'target', default)

    try:
        target_enum = tools.str_to_enum[target_str.lower()]
    except KeyError:
        raise ValueError("The target of the chain must be one of {}"
                         .format(list(tools.str_to_enum.keys())))

    setattr(cfg, 'target', target_enum)


def run_chain(work_root, cfg, start_time, hstart, hstop, job_names):
    """Run chain ignoring already finished jobs.
    
    Sets configuration values derived from user-provided ones, for example the
    folder-structure inside the working directory.

    Sets up the logging module used by the jobs.

    Creates directories for each job.

    Decides which jobs to run and then runs them; first it checks wether the
    job was already executed or is currently running (depending on the logging
    file of the job). Then if the job has to be run, it calls the main()-
    function of the job.
    
    Parameters
    ----------
    work_root : str
        The path to the directory in which the chain writes files during
        execution (typically scratch)
    cfg : config-object
        Object holding all user-configuration parameters as attributes
    start_time : datetime-object
        The startdate of the simulation
    hstart : int
        Offset (in hours) of the actual start from the startdate (start param)
    hstop : int
        Length of simulation (in hours)
    job_names : list of str
        List of the names of jobs to execute on every timeslice.
        Jobs are ``.py`` files in the ``jobs/`` directory with a ``main()``
        function that will be called from ``run_chain()``.
        
        If the list is empty, the default procedure will be executed:
        ``meteo icbc emissions biofluxes int2lm post_int2lm cosmo post_cosmo``
    """
    # ini date and forecast time (ignore meteo times)
    inidate = int((start_time - datetime(1970,1,1)).total_seconds())
    inidate_yyyymmddhh = start_time.strftime('%Y%m%d%H')
    inidate_int2lm_yyyymmddhh = (start_time + timedelta(hours=hstart)
                                ).strftime('%Y%m%d%H')
    forecasttime = '%d' % (hstop - hstart)

    setattr(cfg, 'inidate', inidate)
    setattr(cfg, 'inidate_yyyymmddhh',inidate_yyyymmddhh)
    setattr(cfg, 'forecasttime', forecasttime)
    setattr(cfg, 'hstart', hstart)
    setattr(cfg, 'hstop', hstop)

    # int2lm processing always starts at hstart=0 and we modify inidate instead
    setattr(cfg, 'inidate_int2lm_yyyymmddhh', inidate_int2lm_yyyymmddhh)
    setattr(cfg, 'hstart_int2lm', '0')
    setattr(cfg, 'hstop_int2lm', forecasttime)

    # chain 
    job_id = '%s_%d_%d' % (inidate_yyyymmddhh, hstart, hstop)
    chain_root = os.path.join(work_root, cfg.casename, job_id)
    setattr(cfg, 'chain_root', chain_root)

    # INT2LM
    setattr(cfg, 'int2lm_base', os.path.join(chain_root, 'int2lm'))
    setattr(cfg, 'int2lm_input', os.path.join(chain_root, 'int2lm', 'input'))
    setattr(cfg, 'int2lm_work', os.path.join(chain_root, 'int2lm', 'run'))
    setattr(cfg, 'int2lm_output', os.path.join(chain_root, 'int2lm', 'output'))

    # COSMO
    setattr(cfg, 'cosmo_base', os.path.join(chain_root, 'cosmo'))
    setattr(cfg, 'cosmo_input', os.path.join(chain_root, 'cosmo', 'input'))
    setattr(cfg, 'cosmo_work', os.path.join(chain_root, 'cosmo', 'run'))
    setattr(cfg, 'cosmo_output', os.path.join(chain_root, 'cosmo', 'output'))

    if not cfg.target is tools.Target.COSMOART:
        job_id_last_run = '%s_%d_%d' % (inidate_yyyymmddhh, 
                                        hstart - cfg.restart_step, hstart)
        chain_root_last_run = os.path.join(work_root, cfg.casename,
                                           job_id_last_run)
        setattr(cfg, 'cosmo_restart_in', os.path.join(chain_root_last_run,
                                                      'cosmo', 'restart'))
        setattr(cfg, 'cosmo_restart_out', os.path.join(chain_root, 
                                                       'cosmo', 'restart'))

    if cfg.target is tools.Target.COSMOART:
        # no restarts in cosmoart
        setattr(cfg, 'restart_step', hstop - hstart)

    # if nested run: use output of mother-simulation
    if cfg.target is tools.Target.COSMOART and not os.path.isdir(cfg.meteo_dir):
            # if ifs_hres_dir doesn't point to a directory,
            # it is the name of the mother run
            mother_name = cfg.meteo_dir
            cfg.meteo_dir = os.path.join(work_root,
                                         mother_name,
                                         job_id,
                                         'cosmo',
                                         'output')
            cfg.meteo_inc = 1
            cfg.meteo_prefix = 'lffd'

    # logging
    log_working_dir = os.path.join(chain_root, 'checkpoints', 'working')
    log_finished_dir = os.path.join(chain_root, 'checkpoints', 'finished')
    setattr(cfg, 'log_working_dir', log_working_dir)
    setattr(cfg, 'log_finished_dir', log_finished_dir)

    # create working dirs
    if os.path.exists(chain_root):
        # if chain_root already exists ask user if he wants to continue
        while True:
            inp = input("Target directory of processing chain already exists. "
                        "Continue? ([y]/n) ")
            if inp.lower() == 'y' or inp == '':
                break
            elif inp.lower() == 'n':
                sys.exit()
            else:
                print("Please enter y/n")

    tools.create_dir(chain_root, "chain_root")
    tools.create_dir(log_working_dir, "log_working")
    tools.create_dir(log_finished_dir, "log_finished")

    # run jobs (if required)
    for job in job_names:

        # mapping of scripts in jobs with their arguments

        # if job == 'meteo':
        #     job.meteo.main(start_time, hstart, hstop, cfg)
        #     continue

        skip = False

        # if exists job is currently worked on or has been finished
        if os.path.exists( os.path.join(log_working_dir, job) ):

            while True:
                if os.path.exists( os.path.join(log_finished_dir, job) ):
                    print('Skip "%s" for chain "%s"' % (job, job_id))
                    skip = True
                    break
                else:
                    print('Wait for "%s" of chain "%s"' % (job, job_id))
                    sys.stdout.flush()
                    for _ in range(3000):
                        time.sleep(0.1)

        if not skip:
            print('Process "%s" for chain "%s"' % (job, job_id))
            sys.stdout.flush()
            
            try:
                # Change the log file
                logfile=os.path.join(cfg.log_working_dir,job)
                logfile_finish=os.path.join(cfg.log_finished_dir,job)
                tools.change_logfile(logfile)

                # Launch the job
                to_call = getattr(jobs,job)
                to_call.main(start_time,hstart,hstop,cfg)
                
                shutil.copy(logfile, logfile_finish)

                exitcode=0
            except:
                subject = "ERROR or TIMEOUT in job '%s' for chain '%s'" % (job,
                          job_id)
                logging.exception(subject)
                with open(os.path.join(log_working_dir, job)) as logfile:
                    message = logfile.read()
                tools.send_mail(cfg.mail_address, subject, message)
                raise RuntimeError(subject)
                
            # except AttributeError:
            #     print(job+".py not found so running the bash script instead")
            #     exitcode = call_bash_function(
            #         os.path.join(cfg.chain_src_dir, 'jobs', '%s.bash' % job),
            #         job
            #     )
                
            if exitcode != 0 or not os.path.exists(os.path.join(log_finished_dir, job)):
                subject = "ERROR or TIMEOUT in job '%s' for chain '%s'" % (job,
                          job_id)
                with open(os.path.join(log_working_dir, job)) as logfile:
                    message = logfile.read()
                tools.send_mail(cfg.mail_address, subject, message)
                raise RuntimeError(subject)


def restart_runs(work_root, cfg, start, hstart, hstop, job_names):
    """Starts the subchains in the specified intervals.
    
    Slices the total runtime of the chain according to ``cfg.restart_step``.
    Calls ``run_chain()`` for each step
    
    Parameters
    ----------
    work_root : str
        The path to the directory in which the chain writes files during
        execution (typically scratch)
    cfg : config-object
        Object holding all user-configuration parameters as attributes
    start : datetime-object
        The startdate
    hstart : int
        Offset (in hours) of the actual start from the startdate (start param)
    hstop : int
        Length of simulation (in hours)
    job_names : list of str
        List of the names of jobs to execute on every timeslice.
        Jobs are .py files in the jobs/ directory with a main() function
        that will be called from run_chain().
        
        If the list is empty, the default procedure will be executed:
        meteo icbc emissions biofluxes int2lm post_int2lm cosmo post_cosmo
    """
    # run restarts
    for time in tools.iter_hours(start, hstart, hstop, cfg.restart_step):
        sub_hstart = (time - start).total_seconds() / 3600.0
        runtime = min(cfg.restart_step, hstop - sub_hstart)
        if runtime == 0:
            # don't start simuation with 0 runtime
            continue
        sub_hstop = sub_hstart + runtime

        print("Starting run with starttime {}".format(time))

        run_chain(work_root = work_root,
                  cfg = cfg,
                  start_time = start,
                  hstart = sub_hstart,
                  hstop = sub_hstop,
                  job_names = job_names)


if __name__ == '__main__':
    args = parse_arguments()

    # 'empty' config object to be overwritten by load_config_file
    cfg = None
    for casename in args.casenames:
        cfg = load_config_file(casename=casename, cfg=cfg)
        start_time = datetime.strptime(args.startdate, '%Y-%m-%d')
        set_simulation_type(cfg)
        if args.job_list is None:
            args.job_list = default_jobs[cfg.target]

        print("Starting chain for case {}, using {}".format(casename,
                                                            cfg.target.name))

        if cfg.target is tools.Target.COSMO:
            restart_runs(work_root = cfg.work_root,
                         cfg = cfg,
                         start = start_time,
                         hstart = args.hstart,
                         hstop = args.hstop,
                         job_names = args.job_list)
        elif cfg.target is tools.Target.COSMOART:
            # cosmoart can't do restarts
            run_chain(   work_root = cfg.work_root,
                         cfg = cfg,
                         start_time = start_time,
                         hstart = args.hstart,
                         hstop = args.hstop,
                         job_names = args.job_list)
        else:
            raise RuntimeError("Unknown target: {}".format(cfg.target))

    print('>>> finished chain for good or bad! <<<')
