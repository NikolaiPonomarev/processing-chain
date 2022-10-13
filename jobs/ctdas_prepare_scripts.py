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



    #Copy sbatch template to the working directory

    tools.create_dir(os.path.join(cfg.icon_work, 'template'), "ctdas_icon_templates")
    shutil.copyfile(cfg.ctdas_sbatch_extract_template, os.path.join(cfg.icon_work, 'templates', 'sbatch_extract_template'))

    setattr(
            cfg, 'ctdas_sbatch_extract_template_scratch',
            os.path.join(cfg.icon_work, 'template', 'sbatch_extract_template'))


    starttime_real = starttime + timedelta(hours=hstart)

    
    
    inidata_filename = os.path.join(cfg.icon_input_icbc,
                                    starttime_real.strftime(cfg.meteo_nameformat) + '.nc')

    #Write script files for each ctdas lag

    for time in tools.iter_hours(starttime, hstart, hstop, cfg.ctdas_cycle*24):
        
        current_cycle_ini_date = time.strftime('%Y%m%d%H')
        restart_t = (time - timedelta(hours=cfg.ctdas_cycle*24)).strftime('%Y%m%d%H')

        a = time + timedelta(days=cfg.ctdas_cycle)
        if a < starttime + timedelta(hours=hstop - hstart):
            end_time = a
        else:
            end_time = starttime + timedelta(hours=hstop - hstart)
        
        
        # Write ctdas_extract_template_scratch file
        
        icon_path_var = os.path.join(cfg.icon_base, 'output', 'output_%s_'%(current_cycle_ini_date))
        extracted_file_var = os.path.join(cfg.icon_base, 'extracted','output_%s_'%(current_cycle_ini_date))
        lambda_fs = os.path.join(cfg.icon_base, 'input','oae','lambda_%s_'%(current_cycle_ini_date))
        bg_lambda_fs = os.path.join(cfg.icon_base, 'input','oae','bg_lambda_%s_'%(current_cycle_ini_date))
        restart_folder_opt = os.path.join(cfg.icon_base,'output_%s_opt'%(restart_t))
        restart_folder_prior = os.path.join(cfg.icon_base,'output_%s_prior'%(restart_t))
        restart_file = 'ICON-ART-OEM-INIT_%sT00:00:00.000.nc'%(time.strftime('%Y%m%d%H'))

        with open(cfg.ctdas_extract_template) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work, 'extract_' + current_cycle_ini_date)
        
        setattr(
            cfg, 'suffix',
            'prior')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=icon_path_var+cfg.suffix,
                                fname_base='ICON-ART-OEM-UNSTR',
                                stationdir='/project/s1152/ICONDA/TRANSCOM_INPUT/observations/pool',
                                nneighb=5, 
                                start=time,
                                end=end_time,
                                extracted_file=extracted_file_var+cfg.suffix))

        if os.path.exists(icon_path_var+cfg.suffix,):
            os.system('cp -r %s %s'%(icon_path_var+cfg.suffix, icon_path_var+cfg.suffix+'cycle1'))
        
        if os.path.exists(extracted_file_var+cfg.suffix):
                os.system('cp %s %s'%(output_file+cfg.suffix,output_file+cfg.suffix+'cycle1'))    


        setattr(
            cfg, 'suffix',
            'opt')           
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=icon_path_var+cfg.suffix,
                                fname_base='ICON-ART-OEM-UNSTR',
                                stationdir='/project/s1152/ICONDA/TRANSCOM_INPUT/observations/pool',
                                nneighb=5, 
                                start=time,
                                end=end_time,
                                
                                extracted_file=extracted_file_var))

               
        # Write runscripts

        with open(cfg.icon_runjob) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work, 'runscript_'+ current_cycle_ini_date)


        setattr(
            cfg, 'suffix',
            'prior')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                inifile=inidata_filename,
                                icon_path=icon_path_var+cfg.suffix,
                                lambda_f=lambda_fs+cfg.suffix,
                                bg_lambda=bg_lambda_fs+cfg.suffix,
                                restart_folder=restart_folder_prior,
                                restart_file=restart_file,
                                ini_timestamp=(time-timedelta(hours=24)).strftime('%Y%m%d%H'),
                                st_time=time.strftime(cfg.ctdas_emissions_time_suffix)))

        
        if os.path.exists(output_file+cfg.suffix):
            os.system('mv %s %s'%(output_file+cfg.suffix,output_file+cfg.suffix+'cycle1'))

        setattr(
            cfg, 'suffix',
            'opt')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                inifile=inidata_filename,
                                icon_path=icon_path_var+cfg.suffix,
                                lambda_f=lambda_fs+cfg.suffix,
                                bg_lambda=bg_lambda_fs+cfg.suffix,
                                restart_folder=restart_folder_opt,
                                restart_file=restart_file,
                                ini_timestamp=(time-timedelta(hours=24)).strftime('%Y%m%d%H'),
                                st_time=time.strftime(cfg.ctdas_emissions_time_suffix)))

    exitcode = subprocess.call(
        ["sbatch", "--wait",
         os.path.join(cfg.ctdas_root, 'exec', 'ctdas-icon-' + cfg.ini_datetime_string + '.jb')])

    if exitcode != 0:
        raise RuntimeError("sbatch returned exitcode {}".format(exitcode))
