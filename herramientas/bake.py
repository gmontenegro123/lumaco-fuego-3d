import numpy as np, json
from PIL import Image, ImageFilter, ImageEnhance
Image.MAX_IMAGE_PIXELS=None
O='/home/user/lumaco/pub/'
a=np.transpose(np.load('tci10.npy'),(1,2,0)).astype(np.float32)
dem=np.load('dem30.npy')
H,W_=a.shape[:2]
# hillshade 30 m, sol desde el NE (como en la imagen real), suave
dx=53300/dem.shape[1]; dy=52150/dem.shape[0]
gy,gx=np.gradient(dem,dy,dx); gy=-gy  # y hacia el norte
az=np.radians(50); alt=np.radians(42)
lx,ly,lz=np.sin(az)*np.cos(alt),np.cos(az)*np.cos(alt),np.sin(alt)
z=2.0; nx_,ny_,nz_=-gx*z,-gy*z,np.ones_like(dem); nrm=np.sqrt(nx_**2+ny_**2+nz_**2)
hs=np.clip((nx_*lx+ny_*ly+nz_*lz)/nrm,0,1); flat=lz
Image.fromarray((np.clip(hs/flat*0.72,0,1)*255).astype(np.uint8)).save(O+'hs.jpg',quality=82)
hsU=np.asarray(Image.fromarray((hs/flat).astype(np.float32)).resize((W_,H),Image.BICUBIC))
lo=np.percentile(a[::8,::8],0.5); hi=np.percentile(a[::8,::8],99.7)
a=np.clip((a-lo)/(hi-lo),0,1)**0.72
a*= (0.62+0.38*np.clip(hsU,0.2,1.6))[...,None]
a=np.clip(a*1.06,0,1)
im=Image.fromarray((a*255).astype(np.uint8)); del a
im=ImageEnhance.Color(im).enhance(1.28); im=ImageEnhance.Contrast(im).enhance(1.08)
im=im.filter(ImageFilter.UnsharpMask(radius=1.6,percent=110,threshold=2))
hw,hh=W_//2,H//2; tot=0
for ty in range(2):
    for tx in range(2):
        t=im.crop((tx*hw,ty*hh,(tx+1)*hw,(ty+1)*hh)); p=O+f'sat_{ty}{tx}.jpg'; t.save(p,quality=84,optimize=True); import os; tot+=os.path.getsize(p)
im.resize((2048,2004),Image.LANCZOS).save(O+'sat_lo.jpg',quality=80,optimize=True)
im.resize((1400,1370),Image.LANCZOS).save('/home/user/lumaco/ras/preview2.jpg',quality=75)
# DEM 60 m en PNG (decímetros en R,G)
d=dem[::2,::2]; v=np.clip(np.round(d*10),0,65535).astype(np.uint16)
rgb=np.zeros(v.shape+(3,),np.uint8); rgb[...,0]=v>>8; rgb[...,1]=v&255
Image.fromarray(rgb).save(O+'dem.png',optimize=True)
print('tiles',tot, 'tile px',hw,hh,'dem',v.shape, {f:os.path.getsize(O+f) for f in os.listdir(O)})
