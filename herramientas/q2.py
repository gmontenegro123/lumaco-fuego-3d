import pyarrow.dataset as ds, pyarrow.fs as pafs, pyarrow.compute as pc, pyarrow.parquet as pq, pyarrow as pa, os, sys, time
px=os.environ['HTTPS_PROXY']
fs=pafs.S3FileSystem(anonymous=True, region='us-west-2', proxy_options=px, connect_timeout=20, request_timeout=120)
R='overturemaps-us-west-2/release/2026-10-21.0'
W,S,E,N=-73.37,-38.51,-72.76,-38.04
jobs={'division':('theme=divisions/type=division',['id','subtype','class','names','population','geometry']),
 'place':('theme=places/type=place',['id','names','basic_category','confidence','geometry']),
 'segment':('theme=transportation/type=segment',['id','subtype','class','names','geometry']),
 'water':('theme=base/type=water',['id','subtype','class','names','geometry']),
 'building':('theme=buildings/type=building',['bbox']),
 'landuse':('theme=base/type=land_use',['id','subtype','class','names','geometry']),}
for k in sys.argv[1:]:
    t=time.time(); path,cols=jobs[k]
    try:
        d=ds.dataset(f'{R}/{path}/',filesystem=fs,format='parquet')
        f=(pc.field('bbox','xmin')<E)&(pc.field('bbox','xmax')>W)&(pc.field('bbox','ymin')<N)&(pc.field('bbox','ymax')>S)
        tb=d.to_table(columns=cols,filter=f)
        pq.write_table(tb,f'/home/user/lumaco/ov/{k}.parquet'); print(k,tb.num_rows,round(time.time()-t),'s',len(d.files),'files',flush=True)
    except Exception as e: print(k,'FAIL',str(e)[:500],flush=True)
