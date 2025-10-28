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
compute_account = 'em05'
compute_host = 'eiger'
compute_queue = 'normal'  # 'normal' / 'debug'
constraint = 'mc'  # 'mc' / 'mc'

Init_from_ICON = False

target = 'icon-art-oem'
restart_step = 240000  # hours
restart_cycle_window = 2649600 #2592000 #secs
if constraint == 'mc':
    ntasks_per_node = 4
elif constraint == 'mc':
    ntasks_per_node = 36

# case name = pathname in cases/
path = os.path.realpath(__file__)
casename = os.path.basename(os.path.dirname(path))

# Root directory of the sourcecode of the chain (where run_chain.py is)
chain_src_dir = os.path.join('/capstor/scratch/cscs/nponomar/processing_chain_python/', 'processing-chain')
# chain_src_dir = '/capstor/scratch/cscs/nponomar/processing-chain/'

# Root directory of the working space of the chain
work_root = os.path.join(chain_src_dir, 'work')

# Directory where executables are stored
# exe_dir = "/capstor/scratch/cscs/nponomar/icon-kit/cpu/bin"
# exe_dir =  "/capstor/scratch/cscs/nponomar/icon-gpu/icon-kit/gpu/bin/"
#exe_dir = "/users/nponomar/icon-art-vprm/config/cscs/spack/bin"
exe_dir = '/capstor/scratch/cscs/nponomar/icon-kit/cpu/bin/'

# Case directory
case_dir = os.path.join(chain_src_dir, 'cases', casename)

# PREPARE_DATA ---------------------------------------------------------------
input_root = '/store/empa/em05/input_iconart_processing_chain_example/'

input_root_meteo = '/capstor/scratch/cscs/nponomar/EU_ICBC/era5_data/concatenated/'
meteo_prefix = 'era5_'
meteo_nameformat = meteo_prefix + '%Y%m%d%H'
meteo_suffix = '.nc'
meteo_inc = 1

input_root_chem = '/capstor/scratch/cscs/nponomar/processing_chain_python/processing-chain/work/CAMS_hourly_data/'

input_root_icbc = os.path.join(input_root, 'icbc')
chem_prefix = 'cams73'
chem_nameformat = chem_prefix + '%Y%m%d%H'
chem_suffix = ''
chem_inc = 1

icontools_runjobs = [
    'icontools_remap_ic_runjob.cfg',
    # 'icontools_remap_00_lbc_runjob.cfg',
    # 'icontools_remap_lbc_rest_runjob.cfg',
    # 'icontools_remap_ic_chem_runjob.cfg',
    # 'icontools_remap_lbc_chem_runjob.cfg',
]

# Icontools executables
#icontools_dir = '/project/s903/mjaehn/spack-install/daint/icontools/master/cce/ldcbgsjjzq2p73xbei7ws4wce5ivzxer/bin/'
icontools_dir = '/capstor/scratch/cscs/nponomar/spack-install/daint/icontools/c2sm-master/gcc/a3xbhvwqfcpr2q7n5gx5ucyg5rspepdx/bin'
#icontools_dir = '/capstor/scratch/cscs/nponomar/icon-vprm/bin'
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
input_root_grid_ICOS = '/capstor/scratch/cscs/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022090100_0_9000/icon/input/grid'
radiation_grid_filename = os.path.join(input_root_grid_ICOS,
                                       "icon_europe_DOM01.parent.nc")
dynamics_grid_filename = os.path.join(input_root_grid_ICOS, "icon_europe_DOM01.nc")

input_root_mapping = '/capstor/scratch/cscs/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022090100_0_9000/icon/input/mapping'
map_file_ana = os.path.join(input_root_mapping, "map_file.ana")

map_file_latbc = os.path.join(input_root_mapping, "map_file.latbc")
extpar_filename = os.path.join(
    input_root_grid_ICOS, "icon_extpar_EU_corine_Erik.nc")
input_root_rad = os.path.join(input_root, 'rad')
cldopt_filename = os.path.join(input_root_rad, 'rrtm_cldopt.nc')
lrtm_filename = os.path.join(input_root_rad, 'rrtmg_lw.nc')


# File names -----------------------------------------------------------------
latbc_filename = "era5_<y><m><d><h>_lbc.nc"
inidata_prefix = "era5_init_"
inidata_nameformat = inidata_prefix + '%Y%m%d%H'
inidata_filename_suffix = ".nc"

output_filename = "icon-art-test"
filename_format = "<output_filename>_DOM<physdom>_<datetime2>"

# ART settings----------------------------------------------------------------
input_root_tracers = '/capstor/scratch/cscs/nponomar'
chemtracer_xml_filename = os.path.join(input_root_tracers,
                                       'Hoy_EU.xml')
pntSrc_xml_filename = os.path.join(input_root_tracers, 'pntSrc_example.xml')
art_input_folder = os.path.join(input_root, 'ART_EU')

# OAE ------------------------------------------------------------------------
# Online anthropogenic emissions
oae_dir = '/users/nponomar/Emissions/Hour_of_year/'
oae_gridded_emissions_nc = 'icon_europe_DOM01_with_tno_emissions_HR.nc'
oae_vertical_profiles_nc = 'vertical_profiles_t1_HR.nc'
oae_hourofday_nc = 'hourofday.nc'
oae_dayofweek_nc = 'dayofweek.nc'
oae_monthofyear_nc = 'monthofyear.nc'

oae_hourofyear_nc = 'hourofyear_July22July23_EU_norm.nc'#'hourofyear_23_EU_norm_DST.nc'
lateral_boundary_grid = '/capstor/scratch/cscs/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022090100_0_9000/icon/input/grid/lateral_boundary.grid.nc'
# VPRM ------------------------------------------------------------------------
# ICON-ART VPRM coefficients calculated using MODIS data
online_vprm_dir = '/users/nponomar/MODIS/modis2grid/Data'
#vprm_coeffs_nc = 'VPRM_indices_ICON_EU_22.nc'
vprm_coeffs_nc = 'VPRM_indices_ICON_EU_22_full.nc'
vprm_regions_synth_nc = 'regions_synth.nc' 
vprm_lambdas_synth_nc = 'lambdas_synth.nc'

# vprm_coeffs_nc23 = '/capstor/scratch/cscs/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022070100_0_9000/icon/input/vprm/VPRM_indices_ICON_EU_23Aug_datestr.nc'
vprm_coeffs_nc22 = '/capstor/scratch/cscs/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022081800_0_9000/icon/input/vprm/VPRM_ICON_EU_22_23_datestr.nc'
vprm_coeffs_nc23 = '/capstor/scratch/cscs/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_ERA5_22/2022081800_0_9000/icon/input/vprm/VPRM_ICON_EU_23_datestr.nc'
# SIMULATION =================================================================
# ICON -----------------------------------------------------------------------
# Executable
icon_bin = os.path.join(exe_dir, "icon")
#icon_bin = os.path.join(exe_dir, "icon_oem_emissions")
# Namelists and slurm runscript templates
icon_runjob = os.path.join('/capstor/scratch/cscs/nponomar/processing_chain_python/processing-chain/cases/VPRM_EU_ERA5_22/icon_runjob_res_new_cpu.cfg')
icon_namelist_master = os.path.join(case_dir, 'icon_master.namelist.cfg')
icon_namelist_nwp = os.path.join(case_dir, 'icon_NAMELIST_NWP.cfg')

# Walltimes and domain decomposition
if compute_queue == "normal":
    icon_walltime = "24:00:00"
    icon_np_tot = 16
elif compute_queue == "debug":
    icon_walltime = "00:30:00"
    icon_np_tot = 2
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
