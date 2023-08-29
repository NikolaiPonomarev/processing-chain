#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Prepare initial and boundary conditions
#
# In case of ICON:
# Prepare input for meteorological initial and boundary conditions
# by remapping the files onto the ICON grid (for IC) and the
# auxillary lateral-boundary grid (for BC) with the DWD ICON tools
# and saving them in the input folder.
# Currently, the input files are assumed to be ifs data.
# The files are read-in in grib2-format and the the remapped
# files are saved in netCDF-format (currently only netCDF works
# for ICON when then the simulation is driven by ifs-data).
#
# result in case of success: all meteo input-files necessary are found in
#                            ${int2lm_input}/meteo/
#
# Dominik Brunner, July 2013
#
# 2013-07-16 Initial release, based on Christoph Knote script
# 2017-01-15 Modified for hypatia and project SmartCarb
# 2018-06-21 Translated to Python (kug)
# 2021-02-28 Modified for ICON-simulations (stem)
# 2021-11-12 Modified for ICON-ART-simulations (mjaehn)

import os
import logging
import shutil
import subprocess
from datetime import timedelta
import xarray
from . import tools
import numpy as np

def main(starttime, hstart, hstop, cfg):
    """
    **ICON** (if ``cfg.target`` is ``tools.Target.ICON``)

     Create necessary directories ``cfg.icon_input_icbc``
     and ''cfg.icon_work''

     Submitting the runscript for the DWD ICON tools to remap the meteo files.

     All runscripts specified in ``cfg.icontools_runjobs`` are submitted.

     The meteo files are read-in from the original input directory 
     (``cfg.input_root_meteo``) and the remapped meteo files are
     saved in the input folder on scratch (``cfg.icon_input/icbc``).

     The constant variable 'GEOSP' is added to the files not containing it
     using python-cdo bindings.

    **COSMO**

     Copy meteo files to **int2lm** input.

     Create necessary directory ``cfg.int2lm_input/meteo``. Copy meteo files
     from project directory (``cfg.meteo_dir/cfg.meteo_prefixYYYYMMDDHH``) to
     int2lm input folder on scratch (``cfg.int2lm_input/meteo``).

     For nested runs (meteo files are cosmo-output: ``cfg.meteo_prefix == 
     'lffd'``), also the ``*c.nc``-file with constant parameters is copied.

    
    Parameters
    ----------
    starttime : datetime-object
        The starting date of the simulation
    hstart : int
        Offset (in hours) of the actual start from the starttime
    hstop : int
        Length of simulation (in hours)
    cfg : config-object
        Object holding all user-configuration parameters as attributes
    """

    if cfg.target is tools.Target.ICON or cfg.target is tools.Target.ICONART or \
       cfg.target is tools.Target.ICONARTOEM:

        logging.info('ICON input data (IC/BC)')

        starttime_real = starttime + timedelta(hours=hstart)
       
       #-----------------------------------------------------
        # Create directories
        #-----------------------------------------------------
        tools.create_dir(cfg.icon_work, "icon_work")
        tools.create_dir(cfg.icon_input_icbc, "icon_input_icbc")
        tools.create_dir(cfg.icon_input_grid, "icon_input_grid")
        tools.create_dir(cfg.icon_input_mapping, "icon_input_mapping")
        tools.create_dir(cfg.icon_input_oae, "icon_input_oem")
        tools.create_dir(cfg.icon_input_rad, "icon_input_rad")
        tools.create_dir(cfg.icon_output, "icon_output")
        tools.create_dir(cfg.icon_restart_out, "icon_restart_out")
        tools.create_dir(cfg.icon_input_vprm, "vprm")
        
        #-----------------------------------------------------
        # Copy files
        #-----------------------------------------------------
        # Copy grid files
        tools.copy_file(cfg.radiation_grid_filename,
                        cfg.radiation_grid_filename_scratch,
                        output_log=True)
        tools.copy_file(cfg.dynamics_grid_filename,
                        cfg.dynamics_grid_filename_scratch,
                        output_log=True)
        tools.copy_file(cfg.map_file_latbc,
                        cfg.map_file_latbc_scratch,
                        output_log=True)
        tools.copy_file(cfg.extpar_filename,
                        cfg.extpar_filename_scratch,
                        output_log=True)

        # Copy radiation files
        tools.copy_file(cfg.cldopt_filename,
                        cfg.cldopt_filename_scratch,
                        output_log=True)
        tools.copy_file(cfg.lrtm_filename,
                        cfg.lrtm_filename_scratch,
                        output_log=True)

        # Copy mapping file
        tools.copy_file(cfg.map_file_ana,
                        cfg.map_file_ana_scratch,
                        output_log=True)

        # Copy tracer data in case of ART
        if cfg.target is tools.Target.ICONART or cfg.target is tools.Target.ICONARTOEM:
            tools.create_dir(cfg.icon_input_xml, "icon_input_xml")
            if hasattr(cfg, 'chemtracer_xml_filename'):
                tools.copy_file(cfg.chemtracer_xml_filename,
                                cfg.chemtracer_xml_filename_scratch,
                                output_log=True)
            if hasattr(cfg, 'pntSrc_xml_filename'):
                tools.copy_file(cfg.pntSrc_xml_filename,
                                cfg.pntSrc_xml_filename_scratch,
                                output_log=True)

        if cfg.target is tools.Target.ICONARTOEM:
            tools.copy_file(
                os.path.join(cfg.oae_dir, cfg.oae_gridded_emissions_nc),
                cfg.oae_gridded_emissions_nc_scratch)
            tools.copy_file(
                os.path.join(cfg.oae_dir, cfg.oae_vertical_profiles_nc),
                cfg.oae_vertical_profiles_nc_scratch)
            if hasattr(cfg, 'oae_hourofday_nc'):
                tools.copy_file(
                    os.path.join(cfg.oae_dir, cfg.oae_hourofday_nc),
                    cfg.oae_hourofday_nc_scratch)
            if hasattr(cfg, 'oae_dayofweek_nc'):
                tools.copy_file(
                    os.path.join(cfg.oae_dir, cfg.oae_dayofweek_nc),
                    cfg.oae_dayofweek_nc_scratch)
            if hasattr(cfg, 'oae_monthofyear_nc'):
                tools.copy_file(
                    os.path.join(cfg.oae_dir, cfg.oae_monthofyear_nc),
                    cfg.oae_monthofyear_nc_scratch)
            if hasattr(cfg, 'oae_hourofyear_nc'):
                tools.copy_file(
                    os.path.join(cfg.oae_dir, cfg.oae_hourofyear_nc),
                    cfg.oae_hourofyear_nc_scratch)
            if hasattr(cfg, 'oae_ens_reg_nc'):
                tools.copy_file(os.path.join(cfg.oae_dir, cfg.oae_ens_reg_nc),
                                cfg.oae_ens_reg_nc_scratch)
            if hasattr(cfg, 'oae_ens_lambda_nc'):
                tools.copy_file(
                    os.path.join(cfg.oae_dir, cfg.oae_ens_lambda_nc),
                    cfg.oae_ens_lambda_nc_scratch)
            #VPRM input data
            if hasattr(cfg, 'vprm_coeffs_nc'):
                tools.copy_file(
                    os.path.join(cfg.online_vprm_dir, cfg.vprm_coeffs_nc),
                    cfg.vprm_coeffs_nc_scratch)
            if hasattr(cfg, 'vprm_regions_synth_nc'):
                tools.copy_file(
                    os.path.join(cfg.online_vprm_dir, cfg.vprm_regions_synth_nc),
                    cfg.vprm_regions_synth_nc_scratch)
            if hasattr(cfg, 'vprm_lambdas_synth_nc'):
                tools.copy_file(
                    os.path.join(cfg.online_vprm_dir, cfg.vprm_lambdas_synth_nc),
                    cfg.vprm_lambdas_synth_nc_scratch)


        #-----------------------------------------------------
        # Get datafile lists for LBC (each at 00 UTC and others)
        #-----------------------------------------------------
        datafile_list = []
        datafile_list_rest = []
        datafile_list_chem = []
        datafile_list_ic = []
        datafile_list_ic_chem = []
        for time in tools.iter_hours(starttime, hstart, hstop, cfg.meteo_inc):
            meteo_file = os.path.join(cfg.icon_input_icbc,
                                      time.strftime(cfg.meteo_nameformat))

            #Check if the original input meteo file exists at the given location
            input_meteo_file = os.path.join(cfg.input_root_meteo, time.strftime(cfg.meteo_nameformat)) + cfg.meteo_suffix
            if not os.path.exists(input_meteo_file):
                        raise RuntimeError(
                        "Meteo file does not exist {}".format(input_meteo_file))

            if cfg.target is tools.Target.ICONART or cfg.target is tools.Target.ICONARTOEM:
                chem_file = os.path.join(cfg.icon_input_icbc,
                                         time.strftime(cfg.chem_nameformat))

                #Check if the original input chem file exists at the given location                         
                input_chem_file = os.path.join(cfg.input_root_chem, time.strftime(cfg.chem_nameformat)) + cfg.chem_suffix
                if not os.path.exists(input_chem_file):
                        raise RuntimeError(
                        "Chem file does not exist {}".format(input_chem_file))   

                datafile_list_chem.append(chem_file + cfg.chem_suffix)
            if meteo_file.endswith('00'):
                datafile_list.append(meteo_file + cfg.meteo_suffix)
            else:
                datafile_list_rest.append(meteo_file + cfg.meteo_suffix)
        datafile_list = ' '.join([str(v) for v in datafile_list])
        datafile_list_rest = ' '.join([str(v) for v in datafile_list_rest])
        datafile_list_chem = ' '.join([str(v) for v in datafile_list_chem])
        if hasattr(cfg, 'ctdas_cycle'):
            for time in tools.iter_hours(starttime, hstart, hstop, cfg.ctdas_cycle*24):
                meteo_file_ctdas_ic = os.path.join(cfg.icon_input_icbc,
                                        time.strftime(cfg.meteo_nameformat))
                if cfg.target is tools.Target.ICONART or cfg.target is tools.Target.ICONARTOEM:
                    chem_file_ctdas_ic = os.path.join(cfg.icon_input_icbc,
                                            time.strftime(cfg.chem_nameformat))
                    datafile_list_ic_chem.append(chem_file_ctdas_ic + cfg.chem_suffix)
                datafile_list_ic.append(meteo_file_ctdas_ic + cfg.meteo_suffix)
            datafile_list_ic = ' '.join([str(v) for v in datafile_list_ic])
            datafile_list_ic_chem = ' '.join([str(v) for v in datafile_list_ic_chem])
        else:
            datafile_list_ic = [os.path.join(
                                    cfg.icon_input_icbc,
                                    starttime.strftime(cfg.meteo_nameformat) + '.nc')]
            datafile_list_ic_chem = [os.path.join(
                                        cfg.icon_input_icbc,
                                        starttime.strftime(cfg.chem_nameformat) + '.nc')]

        #-----------------------------------------------------
        # Write and submit runscripts
        #-----------------------------------------------------
        for runscript in cfg.icontools_runjobs:
            logfile = os.path.join(cfg.log_working_dir, 'prepare_data')
            logfile_finish = os.path.join(cfg.log_finished_dir, 'prepare_data')
            with open(os.path.join(cfg.case_dir, runscript)) as input_file:
                to_write = input_file.read()
            output_run = os.path.join(cfg.icon_work, "%s.job" % runscript)
            with open(output_run, "w") as outf:
                outf.write(
                    to_write.format(cfg=cfg,
                                    logfile=logfile,
                                    logfile_finish=logfile_finish,
                                    datafile_list=datafile_list,
                                    datafile_list_rest=datafile_list_rest,
                                    datafile_list_chem=datafile_list_chem,
                                    datafile_list_ic_ctdas = datafile_list_ic,
                                    datafile_list_ic_chem_ctdas = datafile_list_ic_chem))
            exitcode = subprocess.call([
                "sbatch", "--wait",
                os.path.join(cfg.icon_work, "%s.job" % runscript)
            ])
            if exitcode != 0:
                raise RuntimeError(
                    "sbatch returned exitcode {}".format(exitcode))
            logging.info("%s successfully executed." % runscript)
        
        #-----------------------------------------------------
        # Add GEOSP to all meteo files
        #-----------------------------------------------------
        if not cfg.Init_from_ICON:    
            for time in tools.iter_hours(starttime, hstart, hstop, cfg.meteo_inc):
                src_file = os.path.join(
                    cfg.icon_input_icbc,
                    time.strftime(cfg.meteo_nameformat) + '_lbc.nc')
                merged_file = os.path.join(
                    cfg.icon_input_icbc,
                    time.strftime(cfg.meteo_nameformat) + '_merged.nc')
                ds = xarray.open_dataset(src_file)
                # Load GEOSP-dataset as ds_geosp at time 00:
                if (time.hour == 0):
                    da_geosp = ds['GEOSP']
                # Merge GEOSP-dataset with other timesteps
                elif (time.hour != 0):
                    # Change values of time dimension to current time
                    da_geosp = da_geosp.assign_coords(time=[time])
                    # Merge GEOSP into temporary file
                    ds_merged = xarray.merge([ds, da_geosp])
                    ds_merged.attrs = ds.attrs
                    ds_merged.to_netcdf(merged_file)
                    # Rename file to get original file name
                    tools.rename_file(merged_file, src_file)
                    logging.info("Added GEOSP to file {}".format(merged_file))

        #-----------------------------------------------------
        # In case of OEM: merge chem tracers with meteo-files
        #-----------------------------------------------------
        if cfg.target is tools.Target.ICONARTOEM and not cfg.Init_from_ICON:
             
            for time in tools.iter_hours(starttime, hstart, hstop,
                                         cfg.meteo_inc):

                meteo_file = os.path.join(
                        cfg.icon_input_icbc,
                        time.strftime(cfg.meteo_nameformat) + '.nc')
                #if time == starttime:
                if meteo_file in datafile_list_ic:
                    #------------
                    # Merge IC:
                    #------------

                    chem_file = os.path.join(
                        cfg.icon_input_icbc,
                        time.strftime(cfg.chem_nameformat) + '.nc')
                    merged_file = os.path.join(
                        cfg.icon_input_icbc,
                        time.strftime(cfg.meteo_nameformat) + '_merged.nc')
                    ds_meteo = xarray.open_dataset(meteo_file)
                    ds_chem = xarray.open_dataset(chem_file)
                    # LNPS --> PS
                    #ds_chem['PS'] = ds_chem['LNPS']
                    #ds_chem['PS'] = np.exp(ds_chem['LNPS'])
                    #ds_chem['PS'].attrs = ds_chem['LNPS'].attrs
                    #ds_chem['PS'].attrs["long_name"] = 'surface pressure'
                    #GEOP SFC
                    ds_meteo['GEOP_SFC'] = ds_meteo['GEOSP']
                    ds_meteo['GEOP_SFC'].attrs = ds_meteo['GEOSP'].attrs
                    ds_meteo['GEOP_SFC'].attrs["long_name"] = 'surface geopotential'

                    # merge:ds2.isel(nhyi=slice(0, max(ds1.nhyi.values)+1), nhym= slice(0, max(ds1.nhym.values)+1), lev=slice(0, int(max(ds1.lev.values))))
                    try: 
                        ds_merged = xarray.merge([ds_meteo, ds_chem],
                                             compat="override")
                        levels = ds_chem.lev
                        logging.info(
                            "Number of levels in chemical ic/bc is equal to 137")
                    except (ValueError, AttributeError):
                        '''
                        if max(ds_meteo.nhyi.values)>max(ds_chem.nhyi.values):
                            #ds_meteo_reduced = ds_meteo.isel(nhyi=slice(0, max(ds_chem.nhyi.values)+1), nhym= slice(0, max(ds_chem.nhym.values)+1), lev=slice(0, int(max(ds_chem.lev.values)))) 
                            #ds_merged = xarray.merge([ds_meteo_reduced, ds_chem],
                            #                 compat="override")
                        '''
                        ds_meteo = ds_meteo.assign(TRCO2_chemtr=lambda ds_meteo: ds_meteo.T*0)
                        ds_meteo = ds_meteo.assign(CH4_BG=lambda ds_meteo: ds_meteo.T*0)
                        ds_meteo['TRCO2_chemtr'].attrs = ds_chem['TRCO2_chemtr'].attrs
                        ds_meteo['CH4_BG'].attrs = ds_chem['CH4_BG'].attrs
                        #ds_meteo['CH4_BG'] = ds_chem['CH4_BG']
                        start_index = len(ds_meteo.TRCO2_chemtr.values[0]) - len(ds_chem.TRCO2_chemtr.values[0])
                        for x,y in enumerate(ds_meteo.TRCO2_chemtr.values[0]):
                            if x < start_index:
                                    ds_meteo.TRCO2_chemtr[0, x, :] = 0.0
                                    ds_meteo.CH4_BG[0, x, :] = 0.0
                            else:
                                    ds_meteo.TRCO2_chemtr[0, x, :] = ds_chem.TRCO2_chemtr[0, x-start_index, :]
                                    ds_meteo.CH4_BG[0, x, :] = ds_chem.CH4_BG[0, x-start_index, :]
                        
                        ds_meteo.TRCO2_chemtr.values = ds_meteo.TRCO2_chemtr.values/(1.-ds_meteo['QV'].values)
                        ds_meteo.CH4_BG.values = ds_meteo.CH4_BG.values/(1.-ds_meteo['QV'].values)
                        ds_meteo['Q'] = ds_meteo['QV']
                        logging.info(
                            "Number of levels in chemical ic/bc is not equal to 137")

                        ds_merged=ds_meteo
                        '''
                        else:
                            ds_chem_reduced = ds_chem.isel(nhyi=slice(0, max(ds_meteo.nhyi.values)+1), nhym= slice(0, max(ds_meteo.nhym.values)+1), lev=slice(0, int(max(ds_meteo.lev.values))))
                            ds_merged = xarray.merge([ds_meteo, ds_chem_reduced],
                                             compat="override")
                    
                        '''
                    try:    
                        ds_merged['PS'] = ds_merged['PS'].squeeze(dim='lev_2') 
                        ds_merged.to_netcdf(merged_file)
                    except KeyError:
                        ds_merged.to_netcdf(merged_file)
                    #ds_merged.attrs = ds.attrs
                    #ds_merged.to_netcdf(merged_file)
                    # Rename file to get original file name
                    tools.rename_file(merged_file, meteo_file)
                    tools.remove_file(chem_file)
                    logging.info(
                        "Added chemical tracer to file {}".format(merged_file))

                #------------
                # Merge LBC:
                #------------

                meteo_file = os.path.join(
                    cfg.icon_input_icbc,
                    time.strftime(cfg.meteo_nameformat) + '_lbc.nc')
                chem_file = os.path.join(
                    cfg.icon_input_icbc,
                    time.strftime(cfg.chem_nameformat) + '_lbc.nc')
                merged_file = os.path.join(
                    cfg.icon_input_icbc,
                    time.strftime(cfg.meteo_nameformat) + '_merged.nc')
                if os.path.exists(chem_file):
                    ds_meteo = xarray.open_dataset(meteo_file)
                    ds_chem = xarray.open_dataset(chem_file)
                    # LNPS --> PS
                    #ds_chem['PS'] = np.exp(ds_chem['LNPS'])
                    #ds_chem['PS'].attrs = ds_chem['LNPS'].attrs
                    #ds_chem['PS'].attrs["long_name"] = 'surface pressure'
                    ds_chem['TRCH4_chemtr'] = ds_chem['CH4_BG']
                    #ds_chem['TRCO2_chemtr'] = ds_chem['CO2']
                    # merge:
                    try: 
                        ds_merged = xarray.merge([ds_meteo, ds_chem],
                                                compat="override")
                        levels = ds_chem.lev
                    
                    except (ValueError, AttributeError):
                        ds_meteo = ds_meteo.assign(TRCO2_BG_chemtr=lambda ds_meteo: ds_meteo.T*0)
                        ds_meteo = ds_meteo.assign(CH4_BG=lambda ds_meteo: ds_meteo.T*0)
                        ds_meteo['TRCO2_BG_chemtr'].attrs = ds_chem['TRCO2_chemtr'].attrs
                        ds_meteo['CH4_BG'].attrs = ds_chem['CH4_BG'].attrs
                        #ds_meteo['TRCO2_BG_chemtr'] = ds_chem['TRCO2_chemtr']
                        start_index = len(ds_meteo.TRCO2_BG_chemtr.values[0]) - len(ds_chem.TRCO2_chemtr.values[0])
                        #ds_meteo['CH4_BG'] = ds_chem['CH4_BG']
                        for x,y in enumerate(ds_meteo.TRCO2_BG_chemtr.values[0]):
                            if x < start_index:
                                    ds_meteo.TRCO2_BG_chemtr[0, x, :] = 0.0
                                    ds_meteo.CH4_BG[0, x, :] = 0.0
                            else:
                                    ds_meteo.TRCO2_BG_chemtr[0, x, :] = ds_chem.TRCO2_chemtr[0, x-start_index, :]
                                    ds_meteo.CH4_BG[0, x, :] = ds_chem.CH4_BG[0, x-start_index, :]

                        ds_meteo['Q'] = ds_meteo['QV']

                        ds_meteo.TRCO2_BG_chemtr.values = ds_meteo.TRCO2_BG_chemtr.values*(1.-ds_meteo['QV'].values)
                        ds_meteo.CH4_BG.values = ds_meteo.CH4_BG.values*(1.-ds_meteo['QV'].values)
                        ds_merged=ds_meteo
    
                        ds_merged=ds_meteo
                        '''
                        if max(ds_meteo.nhyi.values)>max(ds_chem.nhyi.values):
                            #ds_meteo_reduced = ds_meteo.isel(nhyi=slice(0, max(ds_chem.nhyi.values)+1), nhym= slice(0, max(ds_chem.nhym.values)+1), lev=slice(0, int(max(ds_chem.lev.values)))) 
                            ds_meteo_reduced = ds_meteo.isel(nhyi=slice(0, max(ds_chem.nhyi.values)+1), nhym= slice(0, max(ds_chem.nhym.values)+1))
                            ds_merged = xarray.merge([ds_meteo_reduced, ds_chem],
                                                compat="override")
                        else:
                            #ds_chem_reduced = ds_chem.isel(nhyi=slice(0, max(ds_meteo.nhyi.values)+1), nhym= slice(0, max(ds_meteo.nhym.values)+1), lev=slice(0, int(max(ds_meteo.lev.values))))
                            ds_chem_reduced = ds_chem.isel(nhyi=slice(0, max(ds_meteo.nhyi.values)+1), nhym= slice(0, max(ds_meteo.nhym.values)+1))
                            ds_merged = xarray.merge([ds_meteo, ds_chem_reduced],
                                                compat="override")
                        '''                        
                    try:    
                        ds_merged['PS'] = ds_merged['PS'].squeeze(dim='lev_2') 
                        ds_merged.to_netcdf(merged_file)
                    except KeyError:
                        ds_merged.to_netcdf(merged_file)
                    #ds_merged.attrs = ds.attrs
                    #ds_merged.to_netcdf(merged_file)
                    # Rename file to get original file name
                    tools.rename_file(merged_file, meteo_file)
                    tools.remove_file(chem_file)
                    logging.info(
                        "Added chemical tracer to file {}".format(merged_file))
        else:
            inidata = os.path.join(
                cfg.icon_input_icbc,
                starttime_real.strftime(cfg.meteo_nameformat) + '.nc')
            link = os.path.join(
                cfg.art_input_folder,
                cfg.init_name_5 )   
            os.system('ln -sf ' + inidata + ' ' + link)


    # If COSMO (and not ICON):
    else:
        logging.info('COSMO analysis data for IC/BC')

        dest_path = os.path.join(cfg.int2lm_input, 'meteo')
        tools.create_dir(dest_path, "meteo input")

        source_nameformat = cfg.meteo_nameformat
        starttime_real = starttime + timedelta(hours=hstart)
        if cfg.meteo_prefix == 'lffd':
            # nested runs use cosmoart-output as meteo data
            # have to copy the *c.nc-file
            src_file = os.path.join(
                cfg.meteo_dir,
                starttime_real.strftime(source_nameformat + 'c.nc'))

            tools.copy_file(src_file, dest_path)

            logging.info("Copied constant-param file from {} to {}".format(
                src_file, dest_path))

            # extend nameformat with ending to match cosmo-output
            source_nameformat += '.nc'

        if cfg.meteo_prefix == 'efsf':
            source_nameformat = cfg.meteo_prefix + '%y%m%d%H'

        num_steps = 0
        meteo_dir = cfg.meteo_dir
        subdir = os.path.join(meteo_dir, starttime_real.strftime('%y%m%d%H'))
        for time in tools.iter_hours(starttime, hstart, hstop, cfg.meteo_inc):
            dest_path = os.path.join(cfg.int2lm_input, 'meteo')
            src_file = os.path.join(meteo_dir,
                                    time.strftime(source_nameformat))

            if cfg.meteo_prefix == 'efsf':
                if time == starttime_real:
                    src_file = os.path.join(subdir,
                                            'eas' + time.strftime('%Y%m%d%H'))
                    if not os.path.isfile(src_file) and hasattr(
                            cfg, 'meteo_dir_alt'):
                        meteo_dir = cfg.meteo_dir_alt
                        subdir = os.path.join(
                            meteo_dir, starttime_real.strftime('%y%m%d%H'))
                        src_file = os.path.join(
                            subdir, 'eas' + time.strftime('%Y%m%d%H'))
                    dest_path = os.path.join(cfg.int2lm_input, 'meteo',
                                             cfg.meteo_prefix + '00000000')
                else:
                    td = time - starttime_real - timedelta(hours=6 * num_steps)
                    days = str(td.days).zfill(2)
                    hours = str(td.seconds // 3600).zfill(2)
                    td_total = time - starttime_real
                    days_total = str(td_total.days).zfill(2)
                    hours_total = str(td_total.seconds // 3600).zfill(2)

                    src_file = os.path.join(
                        subdir, cfg.meteo_prefix + days + hours + '0000')
                    dest_path = os.path.join(
                        cfg.int2lm_input, 'meteo',
                        cfg.meteo_prefix + days_total + hours_total + '0000')

                    # Next time, change directory
                    checkdir = os.path.join(meteo_dir,
                                            time.strftime('%y%m%d%H'))
                    if os.path.isdir(checkdir):
                        num_steps += 1
                        subdir = checkdir
                    elif hasattr(cfg, 'meteo_dir_alt'):
                        checkdir = os.path.join(cfg.meteo_dir_alt,
                                                time.strftime('%y%m%d%H'))
                        if os.path.isdir(checkdir):
                            num_steps += 1
                            subdir = checkdir
                            meteo_dir = cfg.meteo_dir_alt
                            logging.info(
                                "Switching to other input directory from {} to {}"
                                .format(cfg.meteo_dir, cfg.meteo_dir_alt))
            elif not os.path.exists(src_file):
                # special case for MeteoSwiss COSMO-7 data
                archive = '/store/mch/msopr/owm/COSMO-7'
                yy = time.strftime("%y")
                path = '/'.join([archive, 'ANA' + yy])
                src_file = os.path.join(path, time.strftime(source_nameformat))

            # copy meteo file from project folder to
            tools.copy_file(src_file, dest_path)

            logging.info("Copied file from {} to {}".format(
                src_file, dest_path))

        # Other IC/BC data
        inv_to_process = []
        if cfg.target is tools.Target.COSMOGHG:
            try:
                CAMS = dict(fullname="CAMS",
                            nickname="cams",
                            executable="cams4int2cosmo",
                            indir=cfg.cams_dir_orig,
                            outdir=cfg.cams_dir_proc,
                            param=cfg.cams_parameters)
                inv_to_process.append(CAMS)
            except AttributeError:
                pass
            try:
                CT = dict(fullname="CarbonTracker",
                          nickname="ct",
                          executable="ctnoaa4int2cosmo",
                          indir=cfg.ct_dir_orig,
                          outdir=cfg.ct_dir_proc,
                          param=cfg.ct_parameters)
                inv_to_process.append(CT)
            except AttributeError:
                pass
        elif cfg.target is tools.Target.COSMOART:
            try:
                MOZART = dict(fullname='MOZART',
                              nickname='mozart',
                              executable='mozart2int2lm',
                              indir=cfg.mozart_file_orig,
                              outdir=cfg.mozart_dir_proc,
                              param=[{
                                  'inc': cfg.mozart_inc,
                                  'suffix': cfg.mozart_prefix
                              }])
                inv_to_process.append(MOZART)
            except AttributeError:
                pass

        if cfg.target is tools.Target.COSMOGHG or cfg.target is tools.Target.COSMOART:
            logging.info("Processing " +
                         ", ".join([i["fullname"]
                                    for i in inv_to_process]) + " data")

            scratch_path = os.path.join(cfg.int2lm_input, 'icbc')
            tools.create_dir(scratch_path, "icbc input")

            for inv in inv_to_process:
                logging.info(inv["fullname"] + " files")
                tools.create_dir(inv["outdir"], "processed " + inv["fullname"])

                for p in inv["param"]:
                    inc = p["inc"]
                    for time in tools.iter_hours(starttime, hstart, hstop,
                                                 inc):
                        logging.info(time)

                        filename = os.path.join(
                            inv["outdir"], p["suffix"] + "_" +
                            time.strftime("%Y%m%d%H") + ".nc")
                        if not os.path.exists(filename):
                            logging.info(filename)
                            try:
                                to_call = getattr(tools, inv["executable"])
                                to_call.main(time, inv["indir"], inv["outdir"],
                                             p)
                            except:
                                logging.error("Preprocessing " +
                                              inv["fullname"] + " data failed")
                                raise

                        # copy to (temporary) run input directory
                        tools.copy_file(filename, scratch_path)

                        logging.info("OK")
