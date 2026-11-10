"""Arma la página publicable (docs/index.html) a partir de la plantilla y los datos.
Uso:  python3 build.py
"""
import json, pathlib
R = pathlib.Path(__file__).parent
t = (R / 'fuente/template.html').read_text(encoding='utf8')
assert '/*DATA*/null' in t
D = json.loads((R / 'datos/lumaco_data2.json').read_text(encoding='utf8'))
D.pop('tex', None)  # la imagen satelital va como archivos aparte en docs/
D['wx'] = json.loads((R / 'datos/clima.json').read_text(encoding='utf8'))
d = json.dumps(D, separators=(',', ':'), ensure_ascii=False)
head = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<style>body{margin:0}img{max-width:100%}</style>\n</head>\n<body>\n')
(R / 'docs/index.html').write_text(head + t.replace('/*DATA*/null', d) + '\n</body>\n</html>\n', encoding='utf8')
print('docs/index.html listo:', len(t) + len(d), 'caracteres')
