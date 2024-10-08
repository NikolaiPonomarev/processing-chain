import os
"""
Configuration file for the 'icon-art-oem-vprm-test' case with ICON-ART
"""

# GENERAL SETTINGS ===========================================================
user = os.environ['USER']
if os.path.exists(os.environ['HOME'] + '/.acct'):
    with open(os.environ['HOME'] + '/.acct', 'r') as file:
        compute_account = file.read().rstrip()
else:
    compute_account = os.popen("id -gn").read().splitlines()[0]
#compute_account = 'em05'
compute_host = 'daint'
compute_queue = 'normal'  # 'normal' / 'debug'
constraint = 'mc'  # 'mc' / 'gpu'
Init_from_ICON = True
target = 'icon-art-oem'
restart_step = 240000  # hours
restart_cycle_window = 604800 #7 days in sec 3600*24*7
if constraint == 'gpu':
    ntasks_per_node = 12
elif constraint == 'mc':
    ntasks_per_node = 36

#Path to the CTDAS root directory
ctdas_root = '/scratch/snx3000/nponomar/ctdas-icon'
Init_from_ICON = False
# case name = pathname in cases/
path = os.path.realpath(__file__)
casename = os.path.basename(os.path.dirname(path))

# Root directory of the sourcecode of the chain (where run_chain.py is)
chain_src_dir = os.path.join('/scratch/snx3000/nponomar/processing_chain_python/', 'processing-chain')

# Root directory of the working space of the chain
work_root = os.path.join(chain_src_dir, 'work')

# Directory where executables are stored
#exe_dir = "/users/nponomar/icon-art-vprm/config/cscs/spack/bin"
exe_dir = "/scratch/snx3000/nponomar/icon-vprm-try2/icon-vprm/bin"
# Case directory
case_dir = os.path.join(chain_src_dir, 'cases', casename)

# PREPARE_DATA ---------------------------------------------------------------
input_root = '/store/empa/em05/input_iconart_processing_chain_example/'

input_root_meteo = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022070100_0_4248/icon/output'
meteo_prefix = 'ICON-ART-UNSTRUCTURED_DOM01_'
#meteo_prefix = 'ICON-ART-OEM_DOM01_'
meteo_nameformat = meteo_prefix + '%Y%m%dT%H'
meteo_suffix = '0000Z.nc'
meteo_inc = 1
remapping_method = 'remapdis' #e.g., remapbil, remapdis
input_root_chem = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022070100_0_4248/icon/output'

input_root_icbc = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022070100_0_4248/icon/output'
chem_prefix = 'ICON-ART-UNSTRUCTURED_DOM01_'
chem_nameformat = chem_prefix + '%Y%m%d'+'T'+'%H'
chem_suffix = '0000Z.nc'
chem_inc = 1

icontools_runjobs = [
    'icontools_remap_ic_runjob.cfg',
    'remap_00_lbc_runjob_py.cfg',
    'remap_lbc_rest_py.cfg'

    #'icontools_remap_00_lbc_runjob.cfg',
    #'icontools_remap_lbc_rest_runjob.cfg',
    #'icontools_remap_ic_chem_runjob.cfg',
    #'icontools_remap_lbc_chem_runjob.cfg',
]

# Icontools executables
#icontools_dir = '/project/s903/mjaehn/spack-install/daint/icontools/master/cce/ldcbgsjjzq2p73xbei7ws4wce5ivzxer/bin/'
icontools_dir = '/scratch/snx3000/nponomar/spack-install/daint/icontools/c2sm-master/gcc/hv7e5pklc6hyntvowrgkywb6rrwzdevb/bin'
iconremap_bin = os.path.join(icontools_dir, "iconremap")
iconsub_bin = os.path.join(icontools_dir, "iconsub")

# Input data for runscript----------------------------------------------------
# Grid
"""#ICON-ART-OEM-TEST
input_root_grid = os.path.join(input_root, 'grids')
#radiation_grid_filename = os.path.join(input_root_grid,
#                                       "testcase_DOM01.parent.nc")
#dynamics_grid_filename = os.path.join(input_root_grid, "testcase_DOM01.nc")
"""
#ICOS EU domain
input_root_grid = os.path.join(input_root, 'grids')
#input_root_grid_ICOS = '/users/nponomar/icon-art/icon/grids'
input_root_grid_ICOS = '/users/nponomar/icon-art/icon/grids/grid_R4B8'
radiation_grid_filename = os.path.join(input_root_grid_ICOS,
                                       "icon_Zurich_R19B9_beo_v3_DOM01.parent.nc")
dynamics_grid_filename = os.path.join(input_root_grid_ICOS, "icon_Zurich_R19B9_beo_v3_DOM01.nc")

input_root_mapping = '/users/nponomar/Mapping'
map_file_ana = os.path.join(input_root_mapping, "map_file_ZH.ana")

map_file_latbc = os.path.join(input_root_mapping, "map_file_ZH.latbc")
extpar_filename = os.path.join(
    input_root_grid_ICOS, "extpar_ZH_beov3_J_merged.nc")
input_root_rad = os.path.join(input_root, 'rad')
cldopt_filename = os.path.join(input_root_rad, 'rrtm_cldopt.nc')
lrtm_filename = os.path.join(input_root_rad, 'rrtmg_lw.nc')
nvlev = 60 #number of vertical levels

# File names -----------------------------------------------------------------
latbc_filename = "ICON-ART-UNSTRUCTURED_DOM01_<y><m><d>T<h>_lbc.nc"
inidata_prefix = "icon_init_"
inidata_nameformat = inidata_prefix + '%Y%m%d%H'
inidata_filename_suffix = ".nc"
mmr = 'wet' #specify the mmr type for latbc, will only be converted if mmr = 'dry'
output_filename = "icon-art-test"
filename_format = "<output_filename>_DOM<physdom>_<ddhhmmss>"

# ART settings----------------------------------------------------------------
input_root_tracers = '/users/nponomar/Emissions/'
chemtracer_xml_filename = os.path.join(input_root_tracers,
                                    #    'vprm_ens_comb.xml')
                                    # 'vprm_bg_ens_test.xml')
                                    'one_cat.xml')
pntSrc_xml_filename = os.path.join(input_root_tracers, 'boundaries_run.xml')
art_input_folder = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/ART'
art_input_folder_bg = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/ART_bg'
# OAE ------------------------------------------------------------------------
# Online anthropogenic emissions
oae_dir = '/scratch/snx3000/nponomar/Emissions/'
oae_gridded_emissions_nc = 'oem_gridded_emissions_HR.nc'
oae_vertical_profiles_nc = 'vertical_profiles_HR.nc'
oae_hourofday_nc = 'hourofday.nc'
oae_dayofweek_nc = 'dayofweek.nc'
oae_monthofyear_nc = 'monthofyear.nc'

oae_hourofyear_nc = 'hourofyear_July22July23_ZH_TNOEU.nc'

# CTDAS ------------------------------------------------------------------------
# rc parameters
ctdas_restart = False
ctdas_BG_run = False
ctdas_cycle = 7
ctdas_nlag = 2
ctdas_nreg_params = 3588 #2547
ctdas_tracer = 'co2'
ctdas_observations = '/scratch/snx3000/nponomar/ICOS_obs_data/Extcrated_obs/Extracted_ZHcyl_obs__20220701_20221223alldates_masl_inlet_cyl.nc'
ctdas_observations_dir = '/scratch/snx3000/nponomar/ICOS_obs_data/Extcrated_obs'
ctdas_dir = '/scratch/snx3000/nponomar/ctdas-icon/exec'
ctdas_obsoperator_home = '/scratch/snx3000/msteiner/ctdas_test/exec/da/rc/stilt'
ctdas_obsoperator_rc = os.path.join(ctdas_obsoperator_home, 'stilt_0.rc')
ctdas_sv_distances = '/scratch/snx3000/nponomar/CTDAS_data/Loc_Cov_matrix_distances_ZH_parent_domain.nc'
ctdas_op_loc_coeffs = '/scratch/snx3000/nponomar/CTDAS_data/Loc_K_matrix_distances_ZH_parent_domain.nc'
ctdas_first_restart_init = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/VPRM_ENSEMBLE_testing/2022070100_0_24/icon/output_32nodes'
ctdas_bg_params = 0
ctdas_first_restart_init_bg = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/CTDAS/2022070200_0_672/icon/output_bg_2022070200_firstsim'
boundaries_xml = '/users/nponomar/Emissions/boundaries_run.xml'
ctdas_datadir = '/scratch/snx3000/nponomar/ICOS_obs_data/Extcrated_obs'
ctdas_system_localization = 'spatial'
ctdas_optimizer_nmembers = 186 #8213 #24000 #186 3540
ctdas_optimizer_nmembers_comb = 186 #54000 #60 * 30 * 30 
ctdas_ncategories = 2
ctdas_nparameters = 3588 #7649 #5094 #17829 #5094 # for example: 13 co2 flux categories: A, RA, GPP * ctdas_nreg_params (number of regions used in data assimilation) + ctdas_bg_params (number of bg regions)
ctdas_obspack_input_dir = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/TRANSCOM_2013_fwd'
ctdas_obs_input_dir = os.path.join(ctdas_datadir, 'core')
ctdas_obs_input_fname = 'obs_forecast.nc'
ctdas_regtype = 'olson19_oif30'
ctdas_regionsfile = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/CTDAS_ZH/2022120100_0_840/icon/input/vprm/Regions_ZH_parent_domain_indcs_beov3_3cats.nc'
ctdas_obs_sites_rc = os.path.join(ctdas_datadir, 'sites_weights_icos.rc')
ctdas_extract_template = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/runscripts/CTDAS/templates_ZH/extract_template_icos_ZH_one_cat'
cdtdas_extract_boundaries_template = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/runscripts/CTDAS/templates_ZH/extract_boundaries_template_icos_ZH'
ctdas_boundary_lamdas_file = '/scratch/snx3000/nponomar/plt_py/boundary_lambdas_ZH.nc'
ctdas_boundary_mask_file = '/scratch/snx3000/nponomar/plt_py/boundary_mask_ZH_beov3_lbc.nc'
cdtdas_runscript_boundaries_template = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/runscripts/CTDAS/templates_ZH/runscript_template_boundaries_icos_ZH'
ctdas_restart_template = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/runscripts/CTDAS/templates_ZH/runscript_template_icos_ZH_one_cat'
ctdas_sbatch_extract_template = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/runscripts/CTDAS/templates/sbatch_extract_template'
ctdas_emissions_time_suffix = '%Y_%m_%d'
#ctdas_restart_init_time = 86400 #sec

# VPRM ------------------------------------------------------------------------
# ICON-ART VPRM coefficients calculated using MODIS data
online_vprm_dir = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/input/vprm/'
#vprm_coeffs_nc = 'VPRM_indices_ICON_EU_22.nc'
vprm_coeffs_nc = 'VPRM_indices_ICON_ZH_22Full_Beov3.nc'
vprm_regions_synth_nc = 'Regions_ZH_parent_domain_indcs_beov3_3cats.nc' 
vprm_lambdas_synth_nc = 'Lambdas_for_vprm_ens_co2_185_ZH.nc'
boundary_regions_nc = 'boundary_mask_ZH.nc'

# SIMULATION =================================================================
# ICON -----------------------------------------------------------------------
# Executable
icon_bin = os.path.join(exe_dir, "/scratch/snx3000/nponomar/icon-vprm-try2/icon-vprm/bin/icon_ZH_latest_tested")

# Namelists and slurm runscript templates
icon_runjob = '/scratch/snx3000/nponomar/ICON_ctdas_msteiner/runscripts/CTDAS/templates/runscript_template_restart'
icon_namelist_master = os.path.join(case_dir, 'icon_master.namelist.cfg')
icon_namelist_nwp = os.path.join(case_dir, 'icon_NAMELIST_NWP.cfg')

# Walltimes and domain decomposition
if compute_queue == "normal":
    icon_walltime = "24:00:00"
    icon_np_tot = 32
elif compute_queue == "debug":
    icon_walltime = "00:30:00"
    icon_np_tot = 10
else:
    logging.error("Unknown queue name: %s" % compute_queue)
    sys.exit(1)

# POST-PROCESSING ============================================================
# REDUCE_OUTPUT --------------------------------------------------------------
convert_gas = True
output_levels = 20

# POST_COSMO -----------------------------------------------------------------
# Root directory where the output of the chain is copied to
output_root = os.path.join(chain_src_dir, "output", casename)

# VERIFY_CHAIN ---------------------------------------------------------------
reference_dir = os.path.join(input_root, "reference_output")

# If the output file that gets compared to the reference is not at the location
# that post_icon copied it to, give the path to it here. Else leave it 'None'
#output_dir = None
output_dir = os.path.join(work_root, casename, '2018010100_0_24', 'icon',
                          'output')

# variables_to_check is a dict() with a tuple() of filenames as key and a list
# of variables-names as value. The tuple consists of the filenames of the two
# files to check, the list contains the variable-names that are compared.
# The verify_chain job will look for the files in the reference_dir (first tuple
# element) and the ouput_dir (second tuple element)
values_to_check = {
    ("icon-oem-pgi-20.1.1-cpu-20210215-NWP_LAM_DOM01_01000000.nc", "NWP_LAM_DOM01_01000000.nc"):
    [
        'temp',
        'pres',
        'u',
        'v',
        'w',
        'OEM_tracer_1',
        'OEM_tracer_2',
    ]
}
