import xarray as xr
import pandas as pd
import glob
import numpy as np
import os

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_factor(proFile):
    '''获取垂直分配因子'''
    df = pd.read_csv(proFile)
    keys = []
    power = []
    industry = []
    for i in range(len(df['vglvltop'])):
        k = df['vglvltop'][i]
        keys.append(k)
        power.append(df.loc[i,['power']].values[0])
        industry.append(df.loc[i,['industry']].values[0])
    powerDict = dict(zip(keys,power))
    industryDict = dict(zip(keys,industry))
    return powerDict,industryDict

def vertival_allocate(fileType,emisPath,proFile):
    '''进行垂直层分配'''
    powerDict,industryDict = get_factor(proFile)
    if fileType == 'industry':
        factor = industryDict
    else:
        factor = powerDict
    files = glob.glob(fr"{emisPath}/*_{fileType}_*.nc")
    print(files)
    keysFac = list(factor.keys())
    for file in files:
        datasOut = {}
        with xr.open_dataset(file) as data:
            keys = list(data.keys())
            print(data.dims,keys)
            for k in keys:
                if k != 'TFLAG':
                    print(data[k].shape)
                    datasOut[k] = np.zeros((data[k].shape[0],len(keysFac),data[k].shape[2],data[k].shape[3]))
                    for i in range(len(keysFac)):
                        datasOut[k][:,i,:,:] = data[k][:,0,:,:]*factor[keysFac[i]]
                    datasOut[k] = xr.DataArray(np.array(datasOut[k],dtype = np.float32),dims=data[k].dims,attrs=data[k].attrs)
            datasOut['TFLAG'] = data['TFLAG']  
        outPath = emisPath+'/vertical/'
        check_dir(outPath)
        datasOut = xr.Dataset(datasOut)
        datasOut.attrs = data.attrs
        datasOut.attrs['VGLVLS'] = keysFac
        datasOut.attrs['NLAYS'] = np.int32(len(keysFac))
        print('>>>>>>>>>>>>>>>>>>>>>>>filaname',file.split('/')[-1])
        datasOut.to_netcdf(outPath+file.split('/')[-1])

if __name__ == '__main__':
    proFile = './profile.csv'
    emisPath = './EMIS2'
    sectors = ['power','industry']
    for sec in sectors:
        vertival_allocate(fileType=sec,emisPath=emisPath,proFile=proFile)
