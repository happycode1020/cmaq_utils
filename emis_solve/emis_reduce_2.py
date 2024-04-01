# -*- coding: utf-8 -*-
import os,re
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
from write_total_emis import get_file_list,get_all_emis

def emis_reduce_total(speList,allData,reduceRate,sector):
	'''排放源减排后加和总源清单'''
	reduceTotal = xr.merge(allData,compat='override')
	keys = list(reduceTotal.keys())
	print(keys)
	number = int(re.findall("\d+",sector)[0])
	for k in keys[:]:
		sample = np.zeros(reduceTotal[keys[0]].shape,dtype=np.float32)
		for i in range(len(allData)):
			dimsK = allData[i].dims
			keySect = allData[i].keys()
			if k in keySect:
				attrsK = allData[i][k].attrs
				if k in speList and number==i+1:
					print('>>>>>>>>>>>>k number ',k,number)
					sample = sample+np.array(allData[i][k],dtype=np.float32)*(1-0.2)
				else:
					sample = sample+np.array(allData[i][k],dtype=np.float32)
		reduceTotal[k]=xr.DataArray(sample,dims=dimsK,attrs=attrsK)
	return reduceTotal

def write_total_emis(outPath,dataPath,dateTime,domain,speList,reduceRate,sector):
	'''写出某小时总排放源'''
	fileList=get_file_list(dataPath, dateTime, domain)
	allData = get_all_emis(fileList)
	reduceTotal = emis_reduce_total(speList,allData,reduceRate,sector)
	fileName = f'diag_ar_total_reduce_{domain}_{dateTime}.nc'
	reduceTotal.to_netcdf(path=outPath+'/'+fileName,mode='w',format='NETCDF3_CLASSIC')

def main(startTime,endTime,outPath,dataPath,domain,speList,reduceRate,sector):
	'''批量写总排放量'''
	startTime = datetime.strptime(startTime,'%Y%m%d%H')
	endTime = datetime.strptime(endTime,'%Y%m%d%H')
	while startTime <= endTime:
		dateTime = startTime.strftime('%Y%m%d%H')
		print('>>>>>>>>>>>>>>thisTime ',dateTime)
		write_total_emis(outPath, dataPath, dateTime, domain,speList,reduceRate,sector)
		startTime += timedelta(hours=1)

if __name__ == '__main__':
	dataPath = './data_emission_inventory'
	outPath = './data_emission_inventory'
	startTime = '2019052012'
	endTime = '2019052013'
	domain = 'd02'
	speList = ['NO','NO2']
	reduceRate=0.2
	sector = 'sec02'
	main(startTime,endTime,outPath,dataPath,domain,speList,reduceRate,sector)