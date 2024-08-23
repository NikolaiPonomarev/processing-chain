#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import logging
import os
import subprocess
from .tools import write_cosmo_input_ghg
from . import tools
from datetime import datetime, timedelta


def main(starttime, hstart, hstop, cfg):

    logfile = os.path.join(cfg.log_working_dir, "icon")
    logfile_finish = os.path.join(cfg.log_finished_dir, "icon")

    logging.info("Setup the namelist for an CTDAS ICON run and "
                 "submit the jobs to the queue")

    # Copy icon executable
    execname = 'icon.exe'
    execname_bg = 'icon_bg.exe'
    tools.copy_file(cfg.icon_bin, os.path.join(cfg.icon_work, execname))
    if cfg.ctdas_BG_run:
        tools.copy_file(cfg.icon_bin, os.path.join(cfg.icon_work+'_bg', execname_bg))
    
    setattr(
            cfg, 'ctdas_exec',
            os.path.join(cfg.ctdas_root,
                         'exec'))


    setattr(
            cfg, 'ctdas_rc',
            os.path.join(cfg.ctdas_exec,
                         'ctdas-icon.rc'))
    setattr(
            cfg, 'ctdas_job',
            os.path.join(cfg.ctdas_exec,
                         'ctdas-icon.jb'))
    setattr(
            cfg, 'ctdas_sys_rc',
            os.path.join(cfg.ctdas_exec,
                         'da',
                         'rc',
                         'cteco2',
                         'carbontracker_icon.rc'))

    setattr(
            cfg, 'ctdas_case_rc',
            os.path.join(cfg.ctdas_exec,
                         'ctdas-icon-' + cfg.ini_datetime_string + '.rc'))
    setattr(
            cfg, 'ctdas_case_sys_rc',
            os.path.join(cfg.ctdas_exec,
                         'da',
                         'rc',
                         'cteco2',
                         'carbontracker_icon_' + cfg.ini_datetime_string +'.rc'))

    setattr(
            cfg, 'ctdas_rc',
            os.path.join(cfg.ctdas_exec,
                         'ctdas-icon.rc'))  
            
    setattr(
            cfg, 'ctdas_ini_datetime_string',
            cfg.ini_datetime_string.replace('T', ' ').replace('Z', ''))
    setattr(
            cfg, 'ctdas_end_datetime_string',
            cfg.end_datetime_string.replace('T', ' ').replace('Z', ''))         
    
    # Write ctdas_job.rc file
    with open(cfg.ctdas_rc) as input_file:
        to_write = input_file.read()
    output_file = os.path.join(cfg.ctdas_case_rc)
    with open(output_file, "w") as outf:
        outf.write(
            to_write.format(cfg=cfg))
    # Write ctdas_system.rc file
    with open(cfg.ctdas_sys_rc) as input_file:
        to_write = input_file.read()
    output_file = os.path.join(cfg.ctdas_case_sys_rc)
    with open(output_file, "w") as outf:
        outf.write(
            to_write.format(cfg=cfg))
    # Write ctdas.job file
    with open(cfg.ctdas_job) as input_file:
        to_write = input_file.read()
    output_file = os.path.join(cfg.ctdas_root, 'exec', 'ctdas-icon-' + cfg.ini_datetime_string + '.jb')
    with open(output_file, "w") as outf:
        outf.write(
            to_write.format(cfg=cfg))  

    #Create dir for extracted data
    tools.create_dir(os.path.join(cfg.icon_base, "extracted"), "extracted data")
                                              
    #Create dir for observations and copy them
    tools.create_dir(os.path.join(cfg.icon_base, "input", "observations"), "observations")
    tools.copy_file(cfg.ctdas_observations,
                        os.path.join(cfg.icon_base, "input", "observations")) 

    #ZH case link ini conditions for the first simulation
    inidata = os.path.join(
                    cfg.icon_base,
                    'input',
                    'icbc',
                    starttime.strftime(cfg.meteo_nameformat) + '.nc')
    link = os.path.join(
                    cfg.art_input_folder, #ART input folder same as specified in ICON nml
                    'ART_ICE_iconR19B09-grid_.nc' #ini5 from processing chain
                    )   
    os.system('ln -sf ' + inidata + ' ' + link)
    # inidata_bg = os.path.join(
    #                 cfg.icon_base,
    #                 'input',
    #                 'icbc_bg',
    #                 starttime.strftime(cfg.meteo_nameformat) + '.nc')
    # link_bg = os.path.join(                     #link ini for the bg run
    #                 cfg.art_input_folder_bg, #ART input folder same as specified in ICON nml
    #                 'ART_ICE_iconR19B09-grid_.nc' #ini5 from processing chain
    #                 )   
    # os.system('ln -sf ' + inidata_bg + ' ' + link_bg)

    exitcode = subprocess.call(
        ["sbatch", "--wait",
         os.path.join(cfg.ctdas_root, 'exec', 'ctdas-icon-' + cfg.ini_datetime_string + '.jb')])

    if exitcode != 0:
        raise RuntimeError("sbatch returned exitcode {}".format(exitcode))
