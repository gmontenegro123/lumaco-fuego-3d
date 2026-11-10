# Herramientas de datos

Solo hacen falta para regenerar los datos o las imágenes desde cero. Para el uso normal basta con `build.py` (en la carpeta principal) y `clima.py`.

```
pip install -r herramientas/requirements.txt
cd herramientas
```

Los archivos intermedios son grandes y quedan en la carpeta `trabajo/`, que no se sube a GitHub (se puede cambiar con la variable `LUMACO_TRABAJO`).

| Orden | Programa | Qué hace | Resultado |
|---|---|---|---|
| 1 | `python3 clima.py ../datos/clima.json` | Baja el pronóstico GFS + GEFS de NOAA. | `datos/clima.json` |
| 2 | `python3 hi.py` | Baja la imagen Sentinel-2 a 10 m y el relieve Copernicus a 30 m. | `trabajo/tci10.npy`, `trabajo/dem30.npy` |
| 3 | `python3 bake.py` | Genera las imágenes del sitio a partir del paso 2. | `docs/sat_*.jpg`, `docs/hs.jpg`, `docs/dem.png` |
| 4 | `python3 q2.py division place segment water building` | Baja localidades, caminos, agua y edificaciones de Overture Maps. Tarda varios minutos. | `trabajo/*.parquet` |
| 5 | `python3 pack.py` | Une lo anterior con `datos/lumaco_data.json` (relieve y cobertura a 100 m). | `datos/lumaco_data2.json` |
| 6 | `python3 ../build.py` | Arma la página. | `docs/index.html` |

`prep.py` generó `datos/lumaco_data.json` en la versión 1 a partir de archivos descargados a mano (relieve, WorldCover y Sentinel-2); recibe como argumento la carpeta donde están. `tex.py` generó la imagen de la versión 2 y ya no se usa.

Comprobado el 10 de noviembre de 2026: los pasos 2 y 3 regeneran imágenes idénticas, píxel por píxel, a las publicadas, y los pasos 4 y 5 regeneran exactamente los mismos datos del mapa.
