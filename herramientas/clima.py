"""Descarga el pronóstico GFS 0.25° (NOAA, S3 público) para Lumaco y lo deja como JSON.
Uso: python3 clima.py salida.json     (requiere: pip install eccodes requests numpy)"""
import sys, json, math, time, datetime as dt, concurrent.futures as cf
import requests, numpy as np, eccodes
LAT, LON = -38.20, -72.95
B = 'https://noaa-gfs-bdp-pds.s3.amazonaws.com'
WANT = {'TMP:2 m above ground':'t','RH:2 m above ground':'rh','UGRD:10 m above ground':'u','VGRD:10 m above ground':'v','GUST:surface':'g'}
S = requests.Session()
def get(url, **kw):
    for k in range(4):
        try:
            r = S.get(url, timeout=60, **kw)
            if r.status_code in (200,206): return r
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(2**k)
    return None
def url(run, f): return f"{B}/gfs.{run:%Y%m%d}/{run:%H}/atmos/gfs.t{run:%H}z.pgrb2.0p25.f{f:03d}"
def latest():
    now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    r = now.replace(hour=now.hour//6*6)
    for _ in range(8):
        if get(url(r,168)+'.idx') is not None: return r
        r -= dt.timedelta(hours=6)
    raise SystemExit('sin corrida GFS disponible')
def point(msg):
    h = eccodes.codes_new_from_message(msg)
    try:
        ni = eccodes.codes_get(h,'Ni'); nj = eccodes.codes_get(h,'Nj'); v = eccodes.codes_get_values(h).reshape(nj, ni)
        la0 = eccodes.codes_get(h,'latitudeOfFirstGridPointInDegrees'); dj = (eccodes.codes_get(h,'latitudeOfLastGridPointInDegrees')-la0)/(nj-1); di = 360.0/ni
        y = (LAT-la0)/dj; x = (LON%360)/di; j=int(y); i=int(x); fy=y-j; fx=x-i; i2=(i+1)%ni
        return float((v[j,i]*(1-fx)+v[j,i2]*fx)*(1-fy)+(v[j+1,i]*(1-fx)+v[j+1,i2]*fx)*fy)
    finally: eccodes.codes_release(h)
def one(args):
    run, f = args; u = url(run, f); idx = get(u+'.idx')
    if idx is None: return None
    L = idx.text.strip().split('\n'); out = {}
    for n, line in enumerate(L):
        p = line.split(':'); key = p[3]+':'+p[4]
        if key in WANT:
            a = int(p[1]); b = int(L[n+1].split(':')[1])-1 if n+1 < len(L) else ''
            r = get(u, headers={'Range': f'bytes={a}-{b}'})
            if r is None: return None
            out[WANT[key]] = point(r.content)
    if len(out) < 4: return None
    ws = math.hypot(out['u'], out['v'])*3.6; wd = (math.degrees(math.atan2(-out['u'], -out['v']))+360) % 360
    t = run + dt.timedelta(hours=f)
    return [int(t.timestamp()//3600), round(out['t']-273.15,1), round(out['rh']), round(ws,1), round(wd), round(out.get('g',0)*3.6,1)]
# ---------- Segundo modelo: conjunto GEFS (31 corridas), promedio y dispersión, cada 3 h ----------
G = 'https://noaa-gefs-pds.s3.amazonaws.com'
def gurl(run, kind, f): return f"{G}/gefs.{run:%Y%m%d}/{run:%H}/atmos/pgrb2ap5/{kind}.t{run:%H}z.pgrb2a.0p50.f{f:03d}"
def glatest(first):
    r = first
    for _ in range(6):
        if get(gurl(r,'gespr',168)+'.idx') is not None: return r
        r -= dt.timedelta(hours=6)
    return None
def gone(args):
    run, kind, f = args; u = gurl(run, kind, f); idx = get(u+'.idx')
    if idx is None: return None
    L = idx.text.strip().split('\n'); out = {}
    for n, line in enumerate(L):
        p = line.split(':'); key = p[3]+':'+p[4]
        if key in WANT and WANT[key] != 'g':
            a = int(p[1]); b = int(L[n+1].split(':')[1])-1 if n+1 < len(L) else ''
            r = get(u, headers={'Range': f'bytes={a}-{b}'})
            if r is None: return None
            out[WANT[key]] = point(r.content)
    return (int((run + dt.timedelta(hours=f)).timestamp()//3600), out) if len(out) == 4 else None
def interp(tab, eh):   # tab: lista ordenada de (hora, dict)
    if eh <= tab[0][0]: return tab[0][1]
    if eh >= tab[-1][0]: return tab[-1][1]
    for (a, va), (b, vb) in zip(tab, tab[1:]):
        if a <= eh <= b:
            w = (eh-a)/(b-a) if b > a else 0
            return {k: va[k]*(1-w)+vb[k]*w for k in va}
def blend(rows, run):
    grun = glatest(run)
    if grun is None: return None
    fs = list(range(3, 169, 3))
    with cf.ThreadPoolExecutor(12) as ex:
        avg = [r for r in ex.map(gone, [(grun,'geavg',f) for f in fs]) if r]
        spr = [r for r in ex.map(gone, [(grun,'gespr',f) for f in fs]) if r]
    if len(avg) < 40 or len(spr) < 40: return None
    out = []
    for eh, T, RH, ws, wd, gust in rows:
        if eh < avg[0][0] or eh > avg[-1][0]:
            out.append([eh, T, RH, ws, wd, gust, 0]); continue
        m = interp(avg, eh); s = interp(spr, eh)
        u = -ws/3.6*math.sin(math.radians(wd)); v = -ws/3.6*math.cos(math.radians(wd))
        u2 = (u+m['u'])/2; v2 = (v+m['v'])/2
        ws2 = math.hypot(u2, v2)*3.6; wd2 = (math.degrees(math.atan2(-u2, -v2))+360) % 360
        k = ws2/ws if ws > 1 else 1
        out.append([eh, round((T+m['t']-273.15)/2,1), round((RH+min(100,m['rh']))/2), round(ws2,1), round(wd2), round(gust*min(1.5,max(.6,k)),1), round(math.hypot(s['u'], s['v'])*3.6,1)])
    return out, grun
run = latest(); hrs = list(range(0,121)) + list(range(123,169,3))
with cf.ThreadPoolExecutor(12) as ex: rows = [r for r in ex.map(one, [(run,f) for f in hrs]) if r]
if len(rows) < 100: raise SystemExit(f'pronóstico incompleto: {len(rows)} horas')
fuente = 'NOAA GFS 0,25° (pronóstico global, S3 público)'; campos = ['hora_unix','T_C','HR_pct','viento_kmh','dir_desde_grados','racha_kmh']; extra = {}
try: bl = blend(rows, run)
except Exception as e: bl = None; print('GEFS falló:', e)
if bl:
    rows, grun = bl; fuente = 'NOAA GFS 0,25° combinado con el promedio del conjunto GEFS 0,5° (31 corridas)'; campos.append('incert_viento_kmh'); extra = {'modelos':['GFS','GEFS'], 'corrida_gefs':f'{grun:%Y-%m-%dT%H:00Z}'}
doc = {'fuente':fuente,'corrida':f'{run:%Y-%m-%dT%H:00Z}','generado':dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),'lat':LAT,'lon':LON,'campos':campos,**extra,'h':rows}
json.dump(doc, open(sys.argv[1],'w'), separators=(',',':'))
print(doc['corrida'], extra, len(rows), 'horas', rows[0], rows[15], rows[-1])
