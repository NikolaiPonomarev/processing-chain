import os
import argparse
from multiprocessing import Pool
import xarray as xr
import sys 

import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("remapping_method", type=str, help="the method used for remapping with cdo")
parser.add_argument("output_dir", type=str, help="output directory")
parser.add_argument("input_dir", type=str, help="path to the data that is being remapped")
parser.add_argument("datalist", type=str, help="the list containing full file names which will be created after remapping")

args = parser.parse_args()
remapping_method = args.remapping_method
input_dir = args.input_dir
output_dir = args.output_dir
datalist = args.datalist
#print('!!!!METHOD', remapping_method)
#print('!!!!Output_dir', output_dir)
#print('DATALIST IS : ', datalist)

def remap_lbc_rest(file):
    print('Remapping data from the file:', file, 'using cdo method:', remapping_method)
    input_file_name = input_dir +'/'+ os.path.basename(file)
    output_file_name = output_dir +'/'+ os.path.basename(file)[:-8] + '_lbc.nc'
    print('LBC_rest_file_name is ', output_file_name)
    #print('cdo setpartabn,/scratch/snx3000/nponomar/Emissions/mypartab_lbc,convert -selname,pres,temp,u,v,w,qv,qi,qr,qc,qs,fis,geopot,rho,theta_v,z_ifc,CO2_RA,CO2_GPP,TRCO2_BG_chemtr,TRCO2_Anthropogenic_chemtr ' + file + ' tmp200.nc')
    #print('cdo -s '+remapping_method+',triangular-grid_00_lbc.nc -selname,PS,T,U,V,W,QV,QI,QR,QC,QS,GEOSP,GEOP_ML,DEN,THETA_V,HHL,CO2_RA,CO2_GPP,TRCO2_BG_chemtr,TRCO2_A_chemtr tmp200.nc ' + output_file_name)
    #print('ncrename -d cell,ncells ' +output_file_name)
    #print('ncrename -d nv,vertices ' +output_file_name)
    os.system('cdo -L setpartabn,/scratch/snx3000/nponomar/Emissions/mypartab_lbc,convert -selname,pres,temp,u,v,w,qv,qi,qr,qc,qs,fis,geopot,rho,theta_v,z_ifc,CO2_RA,CO2_GPP,TRCO2_BG_chemtr,TRCO2_Anthropogenic_chemtr ' + input_file_name + ' tmplbc'+os.path.basename(file)[:-8]+'.nc')
    os.system('cdo -s -L '+remapping_method+',triangular-grid_lbc.nc -selname,PS,T,U,V,W,QV,QI,QR,QC,QS,GEOSP,GEOP_ML,DEN,THETA_V,TRCO2_BG_RA,TRCO2_BG_GPP,TRCO2_BG,TRCO2_BG_A' + ' tmplbc'+os.path.basename(file)[:-8]+'.nc ' +  output_file_name)
    os.system('ncrename -d cell,ncells ' +output_file_name)
    os.system('ncrename -d nv,vertices ' +output_file_name)
    os.remove('tmplbc'+os.path.basename(file)[:-8]+'.nc')
    # ds = xr.open_dataset(output_file_name)
    # ds['TRCO2_BG'] = ds['TRCO2_A_chemtr'] + ds['TRCO2_BG_chemtr'] + ds['CO2_RA'] - ds['CO2_GPP']
    # ds = ds.drop(['TRCO2_A_chemtr', 'TRCO2_BG_chemtr', 'CO2_RA', 'CO2_GPP'])
    # ds.to_netcdf(output_file_name)
    

if __name__ == '__main__':
    file_list = open(datalist, 'r')
    l = file_list.readlines()
    args1 =  l[0].split()
    with Pool(12) as pool:
        M = list(pool.map(remap_lbc_rest, args1)) 




