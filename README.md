# Lumaco Fuego 3D

Simulador 3D de propagación de incendios forestales y coordinación interinstitucional para la comuna de Lumaco, Región de La Araucanía, Chile.

**Estado: prototipo, versión 6 (10 de noviembre de 2026).** El modelo de propagación usa coeficientes de referencia **sin calibrar** con incendios reales de la zona. Sirve para comparar escenarios y coordinar; no sirve para decidir evacuaciones ni reemplaza el análisis de CONAF.

## Qué hace

- Muestra el relieve de la comuna en 3D con imagen satelital (Sentinel-2, 10 m), caminos, ríos, localidades, edificaciones y servicios.
- Proyecta el avance de un incendio hasta 24 horas desde un foco o desde un perímetro dibujado, según combustible, pendiente, viento, temperatura y humedad.
- Usa el pronóstico del tiempo hora a hora (NOAA GFS y GEFS) o un escenario manual (por ejemplo, día crítico 30-30-30 o viento puelche).
- Permite trazar cortafuegos, considerar el freno de los caminos y activar un escenario El Niño.
- Estima la hora de llegada del fuego a cada localidad y cuáles quedarían con la salida cortada.
- Lleva el registro de brigadas y máquinas por institución, una bitácora, y exporta la situación en KML y la bitácora en CSV.

## Contenido del repositorio

| Carpeta o archivo | Qué contiene |
|---|---|
| `docs/` | **El sitio listo para publicar**: `index.html` (la aplicación con los datos incluidos) y las 7 imágenes que usa (satélite, sombreado y relieve). |
| `fuente/template.html` | El código de la aplicación (HTML, CSS y JavaScript en un solo archivo). Tiene el marcador `/*DATA*/null` donde se insertan los datos. |
| `build.py` | Arma `docs/index.html` a partir de la plantilla y los datos. |
| `datos/lumaco_data2.json` | Datos de la grilla de 560 × 520 celdas (~100 m): elevación, cobertura del suelo, localidades, caminos, agua, edificaciones, puntos de interés y límite comunal. |
| `datos/clima.json`, `docs/clima.json` | Último pronóstico descargado. Lo renueva la tarea automática cada 6 horas; la página lee la copia de `docs/`. |
| `.github/workflows/clima.yml` | La tarea automática de GitHub que renueva el pronóstico. |
| `datos/lumaco.geojson`, `datos/lumaco_data.json` | Límite comunal y datos de la versión 1. Se conservan como referencia; ya no se usan al armar la página. |
| `herramientas/` | Programas que generaron los datos: `prep.py`, `q2.py`, `pack.py`, `tex.py`, `hi.py`, `bake.py` y `clima.py` (pronóstico). |
| `pruebas/` | Pruebas automáticas con navegador (`shot.js`) y hoja de miniaturas de recursos (`icons.html`). |

## Cómo verlo

Abrir `docs/index.html` directamente con doble clic **no funciona** (el navegador bloquea las imágenes). Hay que servir la carpeta:

```
cd docs
python3 -m http.server 8000
```

y abrir `http://localhost:8000` en el navegador. Se necesita conexión a internet, porque la página carga la biblioteca three.js y las tipografías desde la red.

### Publicarlo con GitHub Pages

El sitio está preparado para GitHub Pages, pero **Pages no está activado**. Para activarlo: en GitHub, *Settings → Pages → Build and deployment → Deploy from a branch*, elegir la rama principal y la carpeta `/docs`. El enlace quedará como `https://gmontenegro123.github.io/lumaco-fuego-3d/`.

A tener en cuenta antes de activarlo:

- Un sitio de GitHub Pages es **visible para cualquiera que tenga el enlace**, aunque el repositorio sea privado.
- Con una cuenta gratuita de GitHub, Pages solo está disponible si el repositorio es público.

### Diferencias con la versión publicada en claude.ai

Fuera de claude.ai la página funciona en **modo local**:

- Los recursos, la bitácora y el escenario se guardan solo en el navegador de cada persona. **No se comparten** entre instituciones.
- El pronóstico se renueva solo: una tarea automática de GitHub (`.github/workflows/clima.yml`) descarga cada 6 horas el pronóstico de NOAA (GFS y GEFS, las mismas fuentes que la versión de claude.ai) y lo guarda en `docs/clima.json`. La página lo lee al abrirse y lo vuelve a consultar cada 30 minutos. El modelo de NOAA publica una corrida nueva cada 6 horas, así que no existe un dato más reciente que ese.
- Las exportaciones KML y CSV se muestran como texto para copiar, en vez de descargarse.

La versión con datos compartidos en vivo sigue siendo la publicada en claude.ai.

## Cómo rearmar la página

```
python3 build.py
```

Lee `fuente/template.html`, `datos/lumaco_data2.json` y `datos/clima.json`, y escribe `docs/index.html`.

Para refrescar antes el pronóstico:

```
pip install eccodes requests numpy
python3 herramientas/clima.py datos/clima.json
python3 build.py
```

Los demás programas de `herramientas/` y `pruebas/shot.js` conservan rutas del equipo donde se crearon (`/home/user/lumaco/...`); hay que ajustarlas antes de ejecutarlos. Solo hacen falta para regenerar los datos o las imágenes desde cero.

## El modelo

Calcula el tiempo mínimo de llegada del fuego a cada celda de ~100 m (16 direcciones vecinas), con el clima hora a hora. Valores de referencia, sin calibrar:

- Velocidad base de avance (m/min): bosque 1,0; matorral 1,5; pasto 2,0; cultivo 1,2; urbano 0,15; humedal 0,1.
- Viento: multiplica por exp(0,25 · V m/s) a favor, con tope 25; en contra, exp(−0,08 · V) con piso 0,35.
- Pendiente: exp(0,069 · grados), con tope 3.
- Caminos: las rutas principales reducen el avance al 30 % y los caminos secundarios al 50 %. No lo detienen.
- Escenario El Niño: +2 °C, −8 puntos de humedad relativa y 25 % más de combustible fino.

No considera pavesas ni el efecto del combate. La cobertura del suelo usada (WorldCover) no distingue plantación forestal de bosque nativo.

## Fuentes de datos

| Dato | Fuente |
|---|---|
| Relieve | Copernicus DEM GLO-30 (ESA) |
| Imagen satelital | Sentinel-2B, 6 de febrero de 2026, color natural a 10 m (Copernicus) |
| Cobertura del suelo (combustibles) | ESA WorldCover 2021 |
| Localidades, caminos, agua, edificaciones y servicios | Overture Maps, versión 2026-10-21.0 (basado en OpenStreetMap) |
| Límite comunal | Cartografía comunal BCN/IDE, vía repositorio público chile-geojson |
| Clima | NOAA GFS 0,25° y conjunto GEFS 0,5° |

Los nombres, poblaciones y puntos de interés no han sido verificados en terreno.

## Pendientes

- Calibrar el modelo con incendios reales de la zona.
- Incorporar combustibles KITRAL o catastro CONAF, focos activos (NASA FIRMS), ortofotos y posición GPS de los recursos.
- Probar con usuarios y dispositivos reales (hasta ahora solo en navegador simulado).
