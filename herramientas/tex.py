from rutas import *
import os, io, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
from PIL import Image
W,E,S,N=-73.37,-72.76,-38.51,-38.04
TX,TY=4096,4000
t=from_bounds(W,S,E,N,TX,TY)
out=np.zeros((3,TY,TX),np.uint8)
env=gdal_env()
with rasterio.Env(**env):
    for tile in ['XC','YC']:
        u=f'/vsicurl/https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/18/H/{tile}/2026/2/S2B_18H{tile}_20260206_0_L2A/TCI.tif'
        with rasterio.open(u) as s:
            print(tile,s.crs,s.width,s.height,flush=True)
            tmp=np.zeros_like(out)
            reproject(rasterio.band(s,[1,2,3]),tmp,dst_transform=t,dst_crs='EPSG:4326',resampling=Resampling.average,src_nodata=0,dst_nodata=0)
            m=tmp.sum(0)>0
            for b in range(3): out[b][m]=tmp[b][m]
print('zero frac',(out.sum(0)==0).mean())
np.save(TRABAJO+'tci.npy',out)
