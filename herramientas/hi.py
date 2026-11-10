from rutas import *
import os, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
W,E,S,N=-73.37,-72.76,-38.51,-38.04
env=gdal_env()
with rasterio.Env(**env):
    # imagen 10 m nativa: 5332 x 5216
    TX,TY=5332,5216; t=from_bounds(W,S,E,N,TX,TY); out=np.zeros((3,TY,TX),np.uint8)
    for tile in ['XC','YC']:
        u=f'/vsicurl/https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/18/H/{tile}/2026/2/S2B_18H{tile}_20260206_0_L2A/TCI.tif'
        with rasterio.open(u) as s:
            tmp=np.zeros_like(out); reproject(rasterio.band(s,[1,2,3]),tmp,dst_transform=t,dst_crs='EPSG:4326',resampling=Resampling.cubic,src_nodata=0,dst_nodata=0)
            m=tmp.sum(0)>0
            for b in range(3): out[b][m]=tmp[b][m]
    np.save(TRABAJO+'tci10.npy',out); print('tci',out.shape,(out.sum(0)==0).mean(),flush=True)
    # DEM 30 m: 1778 x 1740
    DX_,DY_=1778,1740; t=from_bounds(W,S,E,N,DX_,DY_); dem=np.zeros((DY_,DX_),np.float32)
    for lon in ['073','074']:
        u=f'/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_S39_00_W{lon}_00_DEM/Copernicus_DSM_COG_10_S39_00_W{lon}_00_DEM.tif'
        with rasterio.open(u) as s:
            tmp=np.full_like(dem,-9999); reproject(rasterio.band(s,1),tmp,dst_transform=t,dst_crs='EPSG:4326',resampling=Resampling.bilinear,dst_nodata=-9999)
            m=tmp>-9000; dem[m]=tmp[m]
    np.save(TRABAJO+'dem30.npy',dem); print('dem',dem.min(),dem.max(),flush=True)
