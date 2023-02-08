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

    tools.create_dir(os.path.join(cfg.icon_work, 'templates'), "ctdas_icon_templates")
    shutil.copyfile(cfg.ctdas_sbatch_extract_template, os.path.join(cfg.icon_work, 'templates', 'sbatch_extract_template'))

    setattr(
            cfg, 'ctdas_sbatch_extract_template_scratch',
            os.path.join(cfg.icon_work, 'templates', 'sbatch_extract_template'))


    #starttime_real = starttime + timedelta(hours=hstart)

    
    
    #link the first simulation for the restart spin up
    restart_first_sim_init = os.path.join(cfg.ctdas_first_restart_init, 'ICON-ART-UNSTRUCTURED_DOM01_'+'%sT000000Z.nc'%((starttime).strftime('%Y%m%d')))
    link_restart_dir = os.path.join(cfg.icon_base,'output_%s_opt'%((starttime - timedelta(hours=cfg.ctdas_cycle*24)).strftime('%Y%m%d%H')))
    restart_file = os.path.join(link_restart_dir, 'ICON-ART-OEM-INIT_%sT00:00:00.000.nc'%((starttime).strftime('%Y-%m-%d')))
    tools.create_dir(link_restart_dir, "restart ini dir for the first CTDAS simulation")
    os.system('ln -sf ' + restart_first_sim_init + ' ' + restart_file)

    #link the first bg simulation for the restart spin up
    restart_first_sim_init_bg = os.path.join(cfg.ctdas_first_restart_init_bg, 'ICON-ART-UNSTR_'+'%s'%((starttime).strftime('%Y-%m-%d')) + 'T00:00:00.000.nc')
    link_restart_dir_bg = os.path.join(cfg.icon_base,'output_bg_%s_priorcycle1'%((starttime - timedelta(hours=cfg.ctdas_cycle*24)).strftime('%Y%m%d%H')))
    restart_file_bg = os.path.join(link_restart_dir_bg, 'ICON-ART-OEM-INIT_%sT00:00:00.000.nc'%((starttime).strftime('%Y-%m-%d')))
    tools.create_dir(link_restart_dir_bg, "restart ini dir for the first CTDAS simulation")
    os.system('ln -sf ' + restart_first_sim_init_bg + ' ' + restart_file_bg)

    #Write script files for each ctdas lag

    for time in tools.iter_hours(starttime, hstart, hstop, cfg.ctdas_cycle*24):
        
        current_cycle_ini_date = time.strftime('%Y%m%d%H')
        
        restart_t = (time - timedelta(hours=cfg.ctdas_cycle*24)).strftime('%Y%m%d%H')

        a = time + timedelta(days=cfg.ctdas_cycle)
        if a < starttime + timedelta(hours=hstop - hstart):
            end_time = a
        else:
            end_time = starttime + timedelta(hours=hstop - hstart)
        
        inidata_filename = os.path.join(cfg.icon_input_icbc,
                                    (time-timedelta(hours=24)).strftime(cfg.meteo_nameformat) + '.nc')
        # Write ctdas_extract_template_scratch file
        
        icon_path_var = os.path.join(cfg.icon_base, 'output', 'output_%s_'%(current_cycle_ini_date))
        extracted_file_var = os.path.join(cfg.icon_base, 'extracted','output_%s_'%(current_cycle_ini_date))
        extracted_boundary_file_var = os.path.join(cfg.icon_base, 'extracted','output_bg_%s_'%(current_cycle_ini_date))
        lambda_fs = os.path.join(cfg.icon_base, 'input','oae','lambda_%s_'%(current_cycle_ini_date))
        bg_lambda_fs = os.path.join(cfg.icon_base, 'input','oae','bg_lambda_%s_'%(current_cycle_ini_date))
        restart_folder_opt = os.path.join(cfg.icon_base,'output_%s_opt'%(restart_t))
        restart_folder_prior = os.path.join(cfg.icon_base,'output_%s_priorcycle1'%(restart_t))
        restart_file = 'ICON-ART-OEM-INIT_%sT00:00:00.000.nc'%((time).strftime('%Y-%m-%d'))

        with open(cfg.ctdas_extract_template) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work, 'extract_' + current_cycle_ini_date)
        
        setattr(
            cfg, 'suffix',
            'prior')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix,
                                fname_base='ICON-ART-UNSTR',
                                stationdir=cfg.ctdas_observations_dir,
                                nneighb=5, 
                                start=time,
                                end=end_time,
                                extracted_file=extracted_file_var+cfg.suffix))

        setattr(
            cfg, 'suffix',
            'priorcycle1')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix,
                                fname_base='ICON-ART-UNSTR',
                                stationdir=cfg.ctdas_observations_dir,
                                nneighb=5, 
                                start=time,
                                end=end_time,
                                extracted_file=extracted_file_var+cfg.suffix))

        # if os.path.exists(icon_path_var+cfg.suffix,):
        #     os.system('cp -r %s %s'%(icon_path_var+cfg.suffix, icon_path_var+cfg.suffix+'cycle1'))
        
        # if os.path.exists(extracted_file_var+cfg.suffix):
        #         os.system('cp %s %s'%(output_file+cfg.suffix,output_file+cfg.suffix+'cycle1'))    


        setattr(
            cfg, 'suffix',
            'opt')           
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix,
                                fname_base='ICON-ART-UNSTR',
                                stationdir=cfg.ctdas_observations_dir,
                                nneighb=5, 
                                start=time,
                                end=end_time,
                                
                                extracted_file=extracted_file_var+cfg.suffix))

        # Write ctdas_extract_boundary_template_scratch file

        with open(cfg.cdtdas_extract_boundaries_template) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work+'_bg', 'extract_boundaries' + current_cycle_ini_date)
        

        setattr(
            cfg, 'suffix',
            'priorcycle1')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=cfg.icon_output + '_bg_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix,
                                fname_base='ICON-ART-UNSTR',
                                stationdir=cfg.ctdas_observations_dir,
                                nneighb=5, 
                                start=time,
                                end=end_time,
                                extracted_file=extracted_boundary_file_var+cfg.suffix))

        # Write runscripts

        with open(cfg.ctdas_restart_template) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work, 'runscript_'+ current_cycle_ini_date)


        setattr(
            cfg, 'suffix',
            'prior')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                ini_restart_string=(time-timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                ini_restart_end_string=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                inifile=inidata_filename,
                                icon_path=icon_path_var+cfg.suffix,
                                lambda_f=lambda_fs+cfg.suffix + '.nc',
                                bg_lambda=bg_lambda_fs+cfg.suffix + '.nc',
                                restart_folder=restart_folder_prior,
                                restart_file=restart_file,
                                inidata_filename=inidata_filename,
                                output_directory = cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix,
                                ini_timestamp=(time-timedelta(hours=24)).strftime('%Y%m%d%H'),
                                st_time=time.strftime(cfg.ctdas_emissions_time_suffix)))

        tools.create_dir(cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix, "output for priorcycle2 simulations")


        setattr(
            cfg, 'suffix',
            'priorcycle1')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                ini_restart_string=(time-timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                ini_restart_end_string=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                inifile=inidata_filename,
                                icon_path=icon_path_var+cfg.suffix,
                                lambda_f=lambda_fs+cfg.suffix + '.nc',
                                bg_lambda=bg_lambda_fs+cfg.suffix + '.nc',
                                restart_folder=restart_folder_opt,
                                restart_file=restart_file,
                                inidata_filename=inidata_filename,
                                output_directory = cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix,
                                ini_timestamp=(time-timedelta(hours=24)).strftime('%Y%m%d%H'),
                                st_time=time.strftime(cfg.ctdas_emissions_time_suffix)))
        tools.create_dir(cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix, "output for priorcycle1 simulations")
        #if os.path.exists(output_file+cfg.suffix):
        #    os.system('cp %s %s'%(output_file+cfg.suffix,output_file+cfg.suffix+'cycle1'))

        setattr(
            cfg, 'suffix',
            'opt')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                ini_restart_string=(time-timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                ini_restart_end_string=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                inifile=inidata_filename,
                                inidata_filename=inidata_filename,
                                icon_path=icon_path_var+cfg.suffix,
                                lambda_f=lambda_fs+cfg.suffix + '.nc',
                                bg_lambda=bg_lambda_fs+cfg.suffix + '.nc',
                                restart_folder=restart_folder_opt,
                                restart_file=restart_file,
                                output_directory = cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix,
                                ini_timestamp=(time-timedelta(hours=24)).strftime('%Y%m%d%H'),
                                st_time=time.strftime(cfg.ctdas_emissions_time_suffix)))
        tools.create_dir(cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix, "output for optimized simulations")
        # Write runscripts_boundaries
        restart_folder_prior_bg = os.path.join(cfg.icon_base,'output_bg_%s_priorcycle1'%(restart_t))
        restart_file_bg = 'ICON-ART-OEM-INIT_%sT00:00:00.000.nc'%((time).strftime('%Y-%m-%d'))
        inidata_filename_bg = os.path.join(cfg.icon_input_icbc+'_bg',
                            (time-timedelta(hours=24)).strftime(cfg.meteo_nameformat) + '.nc')
        with open(cfg.cdtdas_runscript_boundaries_template) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work+'_bg', 'runscript_boundaries'+ current_cycle_ini_date)

        setattr(
            cfg, 'suffix',
            'priorcycle1')
        with open(output_file+cfg.suffix, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                ini_restart_string=(time-timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                ini_restart_end_string=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                inifile=inidata_filename_bg,
                                icon_path=icon_path_var+cfg.suffix,
                                lambda_f=lambda_fs+cfg.suffix + '.nc',
                                bg_lambda=bg_lambda_fs+cfg.suffix + '.nc',
                                restart_folder=restart_folder_prior_bg,
                                restart_file=restart_file_bg,
                                inidata_filename=inidata_filename_bg,
                                output_directory=cfg.icon_output + '_bg_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix,
                                latbc_bg = cfg.icon_input_icbc+'_bg',
                                ini_timestamp=(time-timedelta(hours=24)).strftime('%Y%m%d%H'),
                                st_time=time.strftime(cfg.ctdas_emissions_time_suffix)))
        tools.create_dir(cfg.icon_output + '_bg_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffix, "output for optimized simulations")
    #exitcode = subprocess.call(
    #    ["sbatch", "--wait",
    #     os.path.join(cfg.ctdas_root, 'exec', 'ctdas-icon-' + cfg.ini_datetime_string + '.jb')])

    #if exitcode != 0:
    #    raise RuntimeError("sbatch returned exitcode {}".format(exitcode))
