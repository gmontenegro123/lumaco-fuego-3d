# Historial de versiones

## Versión 6.1 (10 de noviembre de 2026)

Primera versión preparada para GitHub.

- El pronóstico se renueva solo cada 6 horas con una tarea automática, y la página lo lee al abrirse.
- Si el pronóstico guardado queda con más de 18 horas, GitHub abre un aviso en el repositorio (llega por correo) y lo cierra cuando se normaliza. La página también lo advierte junto a la fuente del pronóstico.
- Revisión automática en cada cambio: se arma la página, se abre en un navegador de prueba y se comprueban la carga, la proyección, los escenarios, los recursos, la bitácora y las exportaciones.
- El cálculo de la propagación es cerca del doble de rápido (de unos 120 a unos 65 milisegundos en el caso más pesado medido), con resultados idénticos.
- Las herramientas que generan los datos y las imágenes ya no dependen del equipo donde se crearon.

## Versión 6.0 (10 de noviembre de 2026)

Igual a la publicada en claude.ai ese día.

- Inicio del incendio desde un perímetro dibujado.
- Los caminos frenan el avance (rutas principales al 30 %, secundarios al 50 %).
- Localidades con la salida cortada por el fuego.
- Bitácora, exportación de la situación en KML y de la bitácora en CSV.
- Miniaturas por tipo de recurso.
- Pronóstico que combina GFS con el conjunto GEFS, con opción de caso desfavorable de viento.

## Versiones 1 a 5 (10 de noviembre de 2026)

- 1: terreno 3D, propagación, cortafuegos, escenario El Niño y recursos compartidos.
- 2: localidades, caminos, agua, edificaciones y puntos de interés (Overture Maps); imagen satelital más detallada.
- 3 y 4: pronóstico automático (GFS) e imagen Sentinel-2 a 10 m con relieve sombreado.
- 5: ajustes previos a la versión 6.
