# -*- coding: utf-8 -*-
import os
import xarray as xr
import numpy as np
from datetime import datetime, timedelta

def get_file_list(dataPath,dateTime,domain):
	'''获取数据'''
	files = os.listdir(dataPath)
	fileList = []
	for f in files:
		if f.startswith('diag'):
			if f.split('.')[0].split('_')[-3].startswith('sec'):
				dtime = f.split('.')[0].split('_')[-1]
				dom = f.split('.')[0].split('_')[-2]
				if dtime == dateTime and dom == domain:
					fileList.append((dataPath+'/'+f))
	return fileList

def get_all_emis(fileList):
	'''某一时刻的数据写出'''
	allData = []
	for f in fileList:
		data = xr.open_dataset(f)
		allData.append(data)
	return allData

def get_total_emis(allData):
	dataTotal = xr.merge(allData,compat='override')
	keys = list(dataTotal.keys())
	print(keys)
	for k in keys:
		sample = np.zeros(dataTotal[keys[0]].shape,dtype=np.float32)
		for dset in allData:
			dimsK = dset.dims
			if k in dset.keys():
				attrsK = dset[k].attrs
				sample = sample+np.array(dset[k],dtype=np.float32)
		dataTotal[k]=xr.DataArray(sample,dims=dimsK,attrs=attrsK)
	return dataTotal

def write_total_emis(outPath,dataPath,dateTime,domain):
	'''写出某小时总排放源'''
	fileList=get_file_list(dataPath, dateTime, domain)
	allData = get_all_emis(fileList)
	dataTotal = get_total_emis(allData)
	fileName = f'diag_ar_total_{domain}_{dateTime}.nc'
	dataTotal.to_netcdf(path=outPath+'/'+fileName,mode='w',format='NETCDF3_CLASSIC')

def main(startTime,endTime,outPath,dataPath,domain):
	'''批量写总排放量'''
	startTime = datetime.strptime(startTime,'%Y%m%d%H')
	endTime = datetime.strptime(endTime,'%Y%m%d%H')
	while startTime <= endTime:
		dateTime = startTime.strftime('%Y%m%d%H')
		print('>>>>>>>>>>>>>>thisTime ',dateTime)
		write_total_emis(outPath, dataPath, dateTime, domain)
		startTime += timedelta(hours=1)

if __name__ == '__main__':
	dataPath = './data_emission_inventory'
	outPath = './data_emission_inventory'
	startTime = '2019052012'
	endTime = '2019052013'
	domain = 'd02'
	dateTime = '2019052012'
	main(startTime,endTime,outPath,dataPath,domain)
	