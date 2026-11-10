import json, base64, io, numpy as np, pyarrow.parquet as pq, shapely.wkb as WKB, os
from shapely.geometry import shape, Point
from PIL import Image
W,S,E,N=-73.37,-38.51,-72.76,-38.04; NX,NY=560,520
D='/home/user/lumaco/ov/'
d=json.load(open('/home/user/lumaco/prev/lumaco_data.json'))
com=shape(json.load(open('/home/user/lumaco/prev/lumaco.geojson'))['geometry'])
q=lambda x,y:(int(round((x-W)*1e5)),int(round((N-y)*1e5)))
def line(g):
    g=g.simplify(0.00008); o=[]
    for x,y in g.coords: o+=q(x,y)
    return o
inb=lambda g: g.intersects(BB)
from shapely.geometry import box; BB=box(W,S,E,N)
# localidades
loc=[]; K={'hamlet':0,'village':1,'town':2}
for r in pq.read_table(D+'division.parquet').to_pylist():
    g=WKB.loads(r['geometry'])
    if not BB.contains(g) or not r['names']: continue
    k=3 if r['subtype']=='neighborhood' else K.get(r['class'],0)
    loc.append([r['names']['primary'],round(g.x,5),round(g.y,5),r['population'],k,1 if com.contains(g) else 0])
print('loc',len(loc),'in comuna',sum(l[5] for l in loc),'pop comuna hamlets+',sum(l[3] or 0 for l in loc if l[5]))
# caminos
RC={'primary':0,'secondary':0,'trunk':0,'motorway':0,'tertiary':1,'unclassified':2,'residential':2,'living_street':2,'unknown':3,'track':3,'service':3}
roads=[]
for r in pq.read_table(D+'segment.parquet').to_pylist():
    if r['subtype']!='road' or r['class'] not in RC: continue
    g=WKB.loads(r['geometry']).intersection(BB)
    if g.is_empty: continue
    for part in (g.geoms if hasattr(g,'geoms') else [g]):
        if part.geom_type=='LineString' and len(part.coords)>1: roads.append([RC[r['class']],line(part)])
print('roads',len(roads),[sum(1 for x in roads if x[0]==c) for c in range(4)])
# agua
wl=[];wp=[]
for r in pq.read_table(D+'water.parquet').to_pylist():
    if r['subtype'] in('ocean','physical','human_made'): continue
    g=WKB.loads(r['geometry']).intersection(BB)
    if g.is_empty: continue
    for part in (g.geoms if hasattr(g,'geoms') else [g]):
        if part.geom_type=='LineString': wl.append([1 if r['subtype']=='river' else 0, line(part)])
        elif part.geom_type=='Polygon': wp.append(line(part.exterior))
print('water',len(wl),len(wp))
# edificaciones
b=pq.read_table(D+'building.parquet').to_pylist(); grid=np.zeros((NY,NX),np.uint16); n=0; nin=0
for r in b:
    x=(r['bbox']['xmin']+r['bbox']['xmax'])/2; y=(r['bbox']['ymin']+r['bbox']['ymax'])/2
    i=int((x-W)/(E-W)*NX); j=int((N-y)/(N-S)*NY)
    if 0<=i<NX and 0<=j<NY: grid[j,i]+=1; n+=1; nin+= com.contains(Point(x,y))
print('bld',n,'in comuna',nin,'max/cell',grid.max())
# puntos de interés
CAT={'elementary_school':'Escuela','education':'Escuela','high_school':'Liceo','middle_school':'Liceo','place_of_learning':'Escuela','hospital':'Salud','health_care':'Salud','emergency_department':'Salud','fire_station':'Bomberos','police_station':'Carabineros','government_office':'Municipio'}
poi=[]
for r in sorted(pq.read_table(D+'place.parquet').to_pylist(),key=lambda r:-(r['confidence'] or 0)):
    c=CAT.get(r['basic_category']); g=WKB.loads(r['geometry'])
    if not c or (r['confidence'] or 0)<0.6 or not com.contains(g): continue
    if any(p[0]==c and abs(p[2]-g.x)<0.004 and abs(p[3]-g.y)<0.004 for p in poi): continue
    poi.append([c,r['names']['primary'],round(g.x,5),round(g.y,5)])
print('poi',poi)
d.update(loc=loc,roads=roads,wl=wl,wp=wp,bld=base64.b64encode(np.minimum(grid,255).astype(np.uint8).tobytes()).decode(),poi=poi)
if os.path.exists('/home/user/lumaco/ras/tci.npy'):
    a=np.load('/home/user/lumaco/ras/tci.npy').astype(np.float32); a=np.transpose(a,(1,2,0))
    lo=np.percentile(a[::8,::8],1); hi=np.percentile(a[::8,::8],99.5)
    a=(np.clip((a-lo)/(hi-lo),0,1)**0.78*255).astype(np.uint8); im=Image.fromarray(a)
    buf=io.BytesIO(); im.save(buf,'JPEG',quality=72,optimize=True); print('jpg',len(buf.getvalue()))
    d['tex']='data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()
    im.resize((1024,1000)).save('/home/user/lumaco/ras/preview.jpg',quality=70)
s=json.dumps(d,separators=(',',':'),ensure_ascii=False); open('/home/user/lumaco/ov/lumaco_data2.json','w').write(s); print('total',len(s))
