from scipy.interpolate import interpn
import xarray as xr
import numpy as np
import os

def check_dir(path):
	if not os.path.exists(path):
		os.makedirs(path)

def compute_pres(etaList):
	'''基于eta层，计算气压层'''
	pbot = 1000  # hpa
	ptop = 500  # hpa
	# eta = (p-ptop)/(pbot-ptop)
	pList = etaList * (pbot - ptop) + ptop
	return pList

def get_lat_lon_vert(grid2dFile):
	'''获取经纬度和垂直坐标'''
	with xr.open_dataset(grid2dFile) as grid2d:
		lat = grid2d['LAT']
		lon = grid2d['LON']
		return lat,lon

def create_tuple(lon,lat,zlevel):
	'''基于一维经纬度、高度层数组，创建三维矩阵，再创建元组'''
	LAT,LON,ZL = np.meshgrid(lat,lon,zlevel)
	lonFlat = LON.T.flatten()
	latFlat = LAT.T.flatten()
	posFlat = ZL.T.flatten()
	pTuple = list(zip(posFlat,latFlat,lonFlat))
	return pTuple

def interp_target(tPlevel,concFile,lat,lon,outPath):
	'''插值到指定层'''
	LAT = np.array(lat)[0,0]
	LON = np.array(lon)[0,0]
	with xr.open_dataset(concFile) as conc:
		print(conc.keys())
		keys = list(conc.keys())
		vert = conc.attrs['VGLVLS']
		pList = compute_pres(vert)
		pList = pList[:-1]
		datas = {}
		for k in keys[:]:
			if k != 'TFLAG':
				print('>>>>>>>>>>>>>>>>>>>>interp:',k)
				data = np.array(conc[k])
				pTuple = create_tuple(LON[0,:],LAT[:,0],tPlevel)
				dT = []
				for t in range(data.shape[0]):
					value = interpn((pList,LAT[:,0],LON[0,:]),data[t],pTuple,method='linear')
					value = np.array(value).reshape((len(tPlevel),len(LAT[:,0]),len(LON[0,:])))
					print(value.shape)
					dT.append(value)
				dT = np.array(dT,dtype=np.float32).reshape((data.shape[0],value.shape[0],value.shape[1],value.shape[2]))
				print(dT.shape)
				datas[k] = xr.DataArray(dT,dims=conc[k].dims,attrs=conc[k].attrs)
		datas['TFLAG'] = conc['TFLAG']
		datas['LAT'] = xr.DataArray(LAT,dims=['ROW','COL'],attrs=lat.attrs)
		datas['LON'] = xr.DataArray(LON,dims=['ROW','COL'],attrs=lon.attrs)
		outPath = outPath+'/interp/'
		check_dir(outPath)
		datas = xr.Dataset(datas)
		datas.attrs = conc.attrs
		datas.attrs['VGLVLS'] = [np.float32(tp) for tp in tPlevel]
		datas.attrs['NLAYS'] = np.int32(len(tPlevel))
		print('>>>>>>>>>>>>>>>>>>>>>>>filaname',concFile.split('/')[-1])
		datas.to_netcdf(outPath+concFile.split('/')[-1])

if __name__ == '__main__':
	grid2dFile = './mcip/GRIDCRO2D_230402.nc'
	outPath = './CMAQ/data/POST'
	# tPlevel = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 925, 1000]
	tPlevel = [1000, 990, 980,  970, 960, 930]
	lat,lon = get_lat_lon_vert(grid2dFile)
	import glob
	files = glob.glob(fr'{outPath}/COMBINE_ACONC_v54_intel_Bench_2016*')
	print(files)
	for file in files:
		interp_target(tPlevel,file,lat,lon,outPath)
