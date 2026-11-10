"""Carpetas que usan las herramientas. Los archivos intermedios (grandes, no se suben a GitHub)
van a trabajo/, o a la carpeta que indique la variable de entorno LUMACO_TRABAJO."""
import os, pathlib
RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATOS = str(RAIZ / 'datos') + '/'
DOCS = str(RAIZ / 'docs') + '/'
_t = pathlib.Path(os.environ.get('LUMACO_TRABAJO', RAIZ / 'trabajo')); _t.mkdir(parents=True, exist_ok=True)
TRABAJO = str(_t) + '/'
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

def gdal_env():
    """Opciones para leer imágenes remotas con rasterio (con o sin proxy)."""
    e = dict(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif', GDAL_HTTP_MAX_RETRY='4', GDAL_HTTP_RETRY_DELAY='2')
    if PROXY: e['GDAL_HTTP_PROXY'] = PROXY
    ca = os.environ.get('CURL_CA_BUNDLE') or os.environ.get('SSL_CERT_FILE')
    if ca: e['CURL_CA_BUNDLE'] = ca
    return e
