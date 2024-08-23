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



    tools.create_dir(os.path.join(cfg.icon_work, 'templates'), "ctdas_icon_templates")

    #Write runscript files for each restart run and launch the simulation
    setattr(
            cfg, 'suffixprior',
            'prior')
    setattr(
            cfg, 'suffixprior1',
            'priorcycle1')
    setattr(
            cfg, 'suffixopt',
            'opt')

    #Create restart directories
    tools.create_dir(os.path.join(cfg.icon_base, 'restart_' + cfg.suffixprior), "restart_dir_for_prior_emissions")
    tools.create_dir(os.path.join(cfg.icon_base, 'restart_' + cfg.suffixprior1), "restart_dir_for_priorcycle1_emissions")
    tools.create_dir(os.path.join(cfg.icon_base, 'restart_' + cfg.suffixopt), "restart_dir_for_opt_emissions")

    setattr(
            cfg, 'res_folder_prior',
            os.path.join(cfg.icon_base, 'restart_' + cfg.suffixprior))
    setattr(
            cfg, 'res_folder_prior1',
            os.path.join(cfg.icon_base, 'restart_' + cfg.suffixprior1))
    setattr(
            cfg, 'res_folder_opt',
            os.path.join(cfg.icon_base, 'restart_' + cfg.suffixopt))

    #File with initial conditions
    inidata_filename = os.path.join(cfg.icon_input_icbc,
                                    (starttime).strftime(cfg.meteo_nameformat) + '.nc')
    #File with boundary regions
    boundary_mask_file = cfg.ctdas_boundary_mask_file
    
    for time in tools.iter_hours(starttime, hstart, hstop, cfg.restart_cycle_window/(3600)):
        
        current_cycle_ini_date = time.strftime('%Y%m%d%H')



        a = time + timedelta(days=cfg.restart_cycle_window/(3600*24))
        if a < starttime + timedelta(hours=hstop - hstart):
            end_time = a
        else:
            end_time = starttime + timedelta(hours=hstop - hstart)

        #Each restart cycle has only different endtime 
        if time == starttime:
            restart_switch = '.FALSE.'
        else:
            restart_switch = '.TRUE.' 
        if time.year == 2023:
            vegetation_indices_nc = cfg.vprm_coeffs_nc23
        else:
            vegetation_indices_nc =cfg.vprm_coeffs_nc22
        # Write ctdas_extract_template_scratch file

        icon_path_var = os.path.join(cfg.icon_base, 'output', 'output_%s_'%(current_cycle_ini_date))
        extracted_file_var = os.path.join(cfg.icon_base, 'extracted','output_%s_'%(current_cycle_ini_date))
        extracted_boundary_file_var = os.path.join(cfg.icon_base, 'extracted','output_bg_%s_'%(current_cycle_ini_date)) # in this case the same as for the emis file
        lambda_fs = os.path.join(cfg.icon_base, 'input','oae','lambda_%s_'%(current_cycle_ini_date))
        bglambda_fs = os.path.join(cfg.icon_base, 'input','oae','bg_lambda_%s_'%(current_cycle_ini_date))
        logfile = os.path.join(cfg.icon_work, 'icon_'+ current_cycle_ini_date)
        # logfile_finish = os.path.join(cfg.log_finished_dir, "icon" + current_cycle_ini_date)

        with open(cfg.ctdas_extract_template) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work, 'extract_' + current_cycle_ini_date)
        
        with open(output_file+cfg.suffixprior, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixprior,
                                fname_base='ICON-ART-UNSTR',
                                stationdir=cfg.ctdas_observations_dir,
                                nneighb=5,
                                start=time, # + timedelta(hours=1),
                                end=end_time,
                                extracted_file=extracted_file_var+cfg.suffixprior))

        with open(output_file+cfg.suffixprior1, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixprior1,
                                fname_base='ICON-ART-UNSTR',
                                stationdir=cfg.ctdas_observations_dir,
                                nneighb=5,
                                start=time,# + timedelta(hours=1),
                                end=end_time,
                                extracted_file=extracted_file_var+cfg.suffixprior1))
        
        with open(output_file+cfg.suffixopt, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                icon_path=cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixopt,
                                fname_base='ICON-ART-UNSTR',
                                stationdir=cfg.ctdas_observations_dir,
                                nneighb=5, 
                                start=time,# + timedelta(hours=1) ,
                                end=end_time,
                                
                                extracted_file=extracted_file_var+cfg.suffixopt))

        # # Write ctdas_extract_boundary_template_scratch file
        # if time == starttime: 
        #     with open(cfg.cdtdas_extract_boundaries_template) as input_file:
        #         to_write = input_file.read()
        #     output_file = os.path.join(cfg.icon_work+'_bg', 'extract_boundaries' + current_cycle_ini_date)
            
        #     with open(output_file+cfg.suffixprior1, "w") as outf:
        #         outf.write(
        #             to_write.format(cfg=cfg,
        #                             icon_path=cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixprior1,
        #                             fname_base='ICON-ART-UNSTR',
        #                             stationdir=cfg.ctdas_observations_dir,
        #                             nneighb=5, 
        #                             start=time,
        #                             end=end_time,
        #                             extracted_file=extracted_boundary_file_var+cfg.suffixprior1))
        # else:
        #     with open(cfg.cdtdas_extract_boundaries_template) as input_file:
        #         to_write = input_file.read()
        #     output_file = os.path.join(cfg.icon_work+'_bg', 'extract_boundaries' + current_cycle_ini_date)
            
        #     with open(output_file+cfg.suffixprior, "w") as outf:
        #         outf.write(
        #             to_write.format(cfg=cfg,
        #                             icon_path=cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixprior,
        #                             fname_base='ICON-ART-UNSTR',
        #                             stationdir=cfg.ctdas_observations_dir,
        #                             nneighb=5, 
        #                             start=time + timedelta(hours=1),
        #                             end=end_time,
        #                             extracted_file=extracted_boundary_file_var+cfg.suffixprior))                                


        # Write runscripts

        with open(cfg.ctdas_restart_template) as input_file:
            to_write = input_file.read()
        output_file = os.path.join(cfg.icon_work, 'runscript_'+ current_cycle_ini_date)
        ###Do not perturb initial conditions of the second simulation during the first assimilation cycle
        if time == starttime + timedelta(days=cfg.restart_cycle_window/(3600*24)):
            p_ic_prior = '.FALSE.'
        else:
            p_ic_prior = '.TRUE.'
        with open(output_file+cfg.suffixprior, "w") as outf:

            outf.write(
                to_write.format(cfg=cfg,
                                ini_restart_string=(starttime).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                ini_restart_end_string=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                inifile=inidata_filename,
                                restart_switch = restart_switch,
                                icon_path=icon_path_var+cfg.suffixprior,
                                lambda_f=lambda_fs+cfg.suffixprior + '.nc',
                                bgmask=boundary_mask_file,
                                p_ic = p_ic_prior,
                                vegetation_indices_nc=vegetation_indices_nc,
                                bglambda_f=bglambda_fs + cfg.suffixprior + '.nc',
                                logfile = logfile + cfg.suffixprior,
                                restart_file_path=os.path.join(cfg.res_folder_prior, "restart_atm_<rsttime>.nc"),
                                inidata_filename=inidata_filename,
                                output_directory = cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixprior,
                                ))

        tools.create_dir(cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixprior, "output for priorcycle2 simulations")

        with open(output_file+cfg.suffixprior1, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                ini_restart_string=(starttime).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                ini_restart_end_string=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                inifile=inidata_filename,
                                restart_switch = restart_switch,
                                icon_path=icon_path_var+cfg.suffixprior1,
                                logfile = logfile + cfg.suffixprior1,
                                lambda_f=lambda_fs+cfg.suffixprior1 + '.nc',
                                bgmask=boundary_mask_file,
                                p_ic = '.TRUE.', 
                                vegetation_indices_nc=vegetation_indices_nc,
                                bglambda_f=bglambda_fs + cfg.suffixprior1 + '.nc',
                                restart_file_path=os.path.join(cfg.res_folder_prior1, "restart_atm_<rsttime>.nc"),
                                inidata_filename=inidata_filename,
                                output_directory = cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixprior1,
                                ))
        tools.create_dir(cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixprior1, "output for priorcycle1 simulations")

        with open(output_file+cfg.suffixopt, "w") as outf:
            outf.write(
                to_write.format(cfg=cfg,
                                ini_restart_string=(starttime).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                ini_restart_end_string=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                inifile=inidata_filename,
                                restart_switch = restart_switch,
                                icon_path=icon_path_var+cfg.suffixopt,
                                logfile = logfile + cfg.suffixopt,
                                lambda_f=lambda_fs+cfg.suffixopt + '.nc',
                                bgmask=boundary_mask_file,
                                p_ic = '.TRUE.',
                                vegetation_indices_nc=vegetation_indices_nc,
                                bglambda_f=bglambda_fs + cfg.suffixopt + '.nc',
                                restart_file_path=os.path.join(cfg.res_folder_opt, "restart_atm_<rsttime>.nc"),
                                inidata_filename=inidata_filename,
                                output_directory = cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixopt,
                                ))
        tools.create_dir(cfg.icon_output + '_' + (time).strftime('%Y%m%d%H') + '_' + cfg.suffixopt, "output for optimized simulations")

