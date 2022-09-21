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
compute_host = 'daint'
compute_queue = 'normal'  # 'normal' / 'debug'
constraint = 'mc'  # 'mc' / 'gpu'
lam = True
target = 'icon-art-oem'
restart_step = 24  # hours

if constraint == 'gpu':
    ntasks_per_node = 12
elif constraint == 'mc':
    ntasks_per_node = 36

# case name = pathname in cases/
path = os.path.realpath(__file__)
casename = os.path.basename(os.path.dirname(path))

# Root directory of the sourcecode of the chain (where run_chain.py is)
chain_src_dir = os.path.join('/scratch/snx3000/nponomar/processing_chain_python/', 'processing-chain')

# Root directory of the working space of the chain
work_root = os.path.join(chain_src_dir, 'work')

# Directory where executables are stored
exe_dir = "/users/nponomar/icon-art-vprm/config/cscs/spack/bin"

# Case directory
case_dir = os.path.join(chain_src_dir, 'cases', casename)

# PREPARE_DATA ---------------------------------------------------------------
input_root = '/store/empa/em05/input_iconart_processing_chain_example/'
#/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_coupled_not/2018010100_0_24/icon/output/ICON-ART-OEM_DOM01_20180101T030000Z.nc
input_root_meteo = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_coupled_not/2018010100_0_24/icon/output'
meteo_prefix = 'ICON-ART-OEM_DOM01_'
meteo_nameformat = meteo_prefix + '%Y%m%dT%H'
meteo_suffix = '0000Z.nc'
meteo_inc = 1

input_root_chem = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_coupled_not/2018010100_0_24/icon/output'

input_root_icbc = '/scratch/snx3000/nponomar/processing_chain_python/processing-chain/work/VPRM_EU_coupled_not/2018010100_0_24/icon/output'
chem_prefix = 'ICON-ART-OEM_DOM01_'
chem_nameformat = chem_prefix + '%Y%m%d'+'T'+'%H'
chem_suffix = '0000Z.nc'
chem_inc = 1

icontools_runjobs = [
    'icontools_remap_ic_runjob.cfg',
    'icontools_remap_00_lbc_runjob.cfg',
    'icontools_remap_lbc_rest_runjob.cfg',
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
                                       "icon_Zurich_R19B9_DOM01.parent.nc")
dynamics_grid_filename = os.path.join(input_root_grid_ICOS, "icon_Zurich_R19B9_DOM01.nc")

input_root_mapping = '/users/nponomar/Mapping'
map_file_ana = os.path.join(input_root_mapping, "map_file.ana")

map_file_latbc = os.path.join(input_root_mapping, "map_file.latbc")
extpar_filename = os.path.join(
    input_root_grid_ICOS, "icon_extpar_zurich_R19B9.nc")
input_root_rad = os.path.join(input_root, 'rad')
cldopt_filename = os.path.join(input_root_rad, 'rrtm_cldopt.nc')
lrtm_filename = os.path.join(input_root_rad, 'rrtmg_lw.nc')

#ICON-ART-OEM_DOM01_20180101T04_lbc.nc
# File names -----------------------------------------------------------------
latbc_filename = "ICON-ART-OEM_DOM01_<y><m><d>T<h>_lbc.nc"
inidata_prefix = "icon_init_"
inidata_nameformat = inidata_prefix + '%Y%m%d%H'
inidata_filename_suffix = ".nc"

output_filename = "icon-art-test"
filename_format = "<output_filename>_DOM<physdom>_<ddhhmmss>"

# ART settings----------------------------------------------------------------
input_root_tracers = '/users/nponomar/Emissions/'
chemtracer_xml_filename = os.path.join(input_root_tracers,
                                       'tracers_oh_pntsrc.xml')
pntSrc_xml_filename = os.path.join(input_root_tracers, 'pntSrc_example.xml')
art_input_folder = os.path.join(input_root, 'ART')

# OAE ------------------------------------------------------------------------
# Online anthropogenic emissions
oae_dir = '/users/nponomar/Emissions/'
oae_gridded_emissions_nc = 'icon_Zurich_R19B9_DOM01_Emission_CO2_mapLuft_2020_v2021.nc'
oae_vertical_profiles_nc = 'vertical_profiles_c.nc'
oae_hourofday_nc = 'hourofday.nc'
oae_dayofweek_nc = 'dayofweek.nc'
oae_monthofyear_nc = 'monthofyear.nc'

#oae_hourofyear_nc = 'hourofyear.nc'

# VPRM ------------------------------------------------------------------------
# ICON-ART VPRM coefficients calculated using MODIS data
online_vprm_dir = '/users/nponomar/MODIS/modis2grid/Data'
#vprm_coeffs_nc = 'VPRM_indices_ICON_ZH_22.nc'
vprm_coeffs_nc = 'VPRM_indices_icon-art-test.nc'
vprm_regions_synth_nc = 'regions_synth.nc' 
vprm_lambdas_synth_nc = 'lambdas_synth.nc'


# SIMULATION =================================================================
# ICON -----------------------------------------------------------------------
# Executable
icon_bin = os.path.join(exe_dir, "icon")

# Namelists and slurm runscript templates
icon_runjob = os.path.join(case_dir, 'icon_runjob.cfg')
icon_namelist_master = os.path.join(case_dir, 'icon_master.namelist.cfg')
icon_namelist_nwp = os.path.join(case_dir, 'icon_NAMELIST_NWP.cfg')

# Walltimes and domain decomposition
if compute_queue == "normal":
    icon_walltime = "00:30:00"
    icon_np_tot = 16
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
