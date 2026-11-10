import sys, json, base64, io
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
from rasterio.merge import merge
from PIL import Image
D=sys.argv[1]
W,E,S,N=-73.37,-72.76,-38.51,-38.04
NX,NY=560,520
tr=from_bounds(W,S,E,N,NX,NY)
def warp(srcs, nx, ny, rs, dtype, nb=1):
    t=from_bounds(W,S,E,N,nx,ny)
    out=np.zeros((nb,ny,nx),dtype=dtype)
    for p in srcs:
        with rasterio.open(p) as s:
            tmp=np.zeros_like(out)
            reproject(rasterio.band(s,list(range(1,nb+1))) if nb>1 else rasterio.band(s,1), tmp if nb>1 else tmp[0], src_transform=s.transform, src_crs=s.crs, dst_transform=t, dst_crs='EPSG:4326', resampling=rs, src_nodata=0 if nb>1 else None, dst_nodata=0)
            m=tmp.sum(0)>0 if nb>1 else tmp[0]!=0
            for b in range(nb): out[b][m if nb>1 else m]=tmp[b][m]
    return out
dem=warp([D+'/dem_W074.tif',D+'/dem_W073.tif'],NX,NY,Resampling.bilinear,np.float32)[0]
print('dem',dem.min(),dem.max())
lc=warp([D+'/wc.tif'],NX,NY,Resampling.mode,np.uint8)[0]
print('lc',np.unique(lc,return_counts=True))
TX,TY=2048,1578
tci=warp([D+'/tci_XC.tif',D+'/tci_YC.tif'],TX,TY,Resampling.average,np.uint8,3)
print('tci zero frac',(tci.sum(0)==0).mean())
img=Image.fromarray(np.transpose(tci,(1,2,0)))
# mild contrast stretch
a=np.asarray(img).astype(np.float32); lo=np.percentile(a,1); hi=np.percentile(a,99.5)
a=np.clip((a-lo)/(hi-lo)*255*1.0,0,255).astype(np.uint8); img=Image.fromarray(a)
buf=io.BytesIO(); img.save(buf,'JPEG',quality=78); print('jpg',len(buf.getvalue()))
img.save(D+'/../tex_preview.jpg',quality=60)
g=json.load(open(D+'/lumaco.geojson'))['geometry']['coordinates'][0]
pts=g[::2]
# built-up near towns
for name,lat,lon in [('Lumaco',-38.164,-72.913),('Capitán Pastene',-38.198,-73.012)]:
    j=int((N-lat)/(N-S)*NY); i=int((lon-W)/(E-W)*NX)
    win=lc[j-15:j+15,i-15:i+15]; ys,xs=np.where(win==50)
    if len(ys): print(name,'built centroid', N-(j-15+ys.mean()+.5)*(N-S)/NY, W+(i-15+xs.mean()+.5)*(E-W)/NX, len(ys))
    else: print(name,'no built')
el=np.clip(np.round(dem),0,65535).astype('<u2')
out=dict(bbox=[W,S,E,N],nx=NX,ny=NY,elev=base64.b64encode(el.tobytes()).decode(),lc=base64.b64encode(lc.astype(np.uint8).tobytes()).decode(),tex='data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode(),boundary=[[round(p[0],5),round(p[1],5)] for p in pts])
json.dump(out,open(D+'/../lumaco_data.json','w'))
print('sizes',len(out['elev']),len(out['lc']),len(out['tex']))
