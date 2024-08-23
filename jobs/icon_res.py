#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import logging
import os
from re import A
import subprocess
from .tools import write_cosmo_input_ghg
from . import tools
from datetime import datetime, timedelta
import shutil


def main(starttime, hstart, hstop, cfg):
    # Copy icon executable
    execname = 'icon.exe'
    tools.copy_file(cfg.icon_bin, os.path.join(cfg.icon_work, execname))

    #Write runscript files for each restart run and launch the simulation using the default name for the restart file

    for time in tools.iter_hours(starttime, hstart, hstop, cfg.restart_cycle_window/(3600)):
        
        current_cycle_ini_date = time.strftime('%Y%m%d%H')

        logfile = os.path.join(cfg.log_working_dir, "icon" + current_cycle_ini_date)
        logfile_finish = os.path.join(cfg.log_finished_dir, "icon" + current_cycle_ini_date)

        a = time + timedelta(days=cfg.restart_cycle_window/(3600*24))
        if a < starttime + timedelta(hours=hstop - hstart):
            end_time = a
        else:
            end_time = starttime + timedelta(hours=hstop - hstart)
        

        inidata_filename = os.path.join(cfg.icon_input_icbc,
                                    (time).strftime(cfg.meteo_nameformat) + '.nc')

        with open(cfg.icon_runjob) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work, 'runscript_'+ current_cycle_ini_date)

        #Each restart cycle has only different endtime 
        if time == starttime:
            restart_switch = '.FALSE.'
        else:
            restart_switch = '.TRUE.' 
        if time.year == 2023:
            vegetation_indices_nc = cfg.vprm_coeffs_nc23
        else:
            vegetation_indices_nc = cfg.vprm_coeffs_nc22
        with open(output_file, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                restart=restart_switch,
                                ini_restart_string=(starttime).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                ini_restart_end_string=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                inifile=inidata_filename,
                                inidata_filename=inidata_filename,
                                vegetation_indices_nc = vegetation_indices_nc,
                                output_directory = cfg.icon_output,
                                logfile=logfile,
                                logfile_finish=logfile_finish
                                ))
        #ZH case specific, link ini conditions
        if time == starttime:
            inidata = inidata_filename
            link = os.path.join(
                            cfg.art_input_folder, #ART input folder same as specified in ICON nml
                            # 'ART_ICE_iconR19B09-grid_.nc' #ini5 from processing chain
                            cfg.init_file_link
                            )  
            os.system('ln -sf ' + inidata + ' ' + link)

        end_cycle_filename = cfg.icon_output + '/ICON-ART-UNSTRUCTURED_DOM01_%sT000000Z.nc'%((time + timedelta(hours=cfg.restart_cycle_window/(3600))).strftime('%Y%m%d'))
        #Check if the end of the cycle file already exists and if not submit the run icon job
        logging.info("Check for the file :  {}".format(end_cycle_filename))
        if not (os.path.exists(end_cycle_filename)):
            logging.info("Submit Runscript:  {}".format(output_file))
            exitcode = subprocess.call(
                ["sbatch", "--wait",
                os.path.join(cfg.icon_work, output_file)])

            # In case of ICON-ART, ignore the "invalid pointer" error on successful run
            logging.info("Logfile of the last simulation cycle:  {}".format(logfile))
            if tools.grep("free(): invalid pointer", logfile)['success'] and \
            tools.grep("clean-up finished", logfile)['success']:
                exitcode = 0

            if tools.grep("horizontal CFL number exceeded at", logfile)['success']:
                logging.info("CFL error:  {}".format(logfile))

            if exitcode != 0:
                raise RuntimeError("sbatch returned exitcode {}".format(exitcode))
