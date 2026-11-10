// Revisión automática: abre el sitio de docs/ en un navegador sin pantalla y comprueba que
// el mapa carga, la proyección se calcula y las funciones principales responden.
// Uso (desde pruebas/):  npm install && node humo.js
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const DOCS = path.join(__dirname, '..', 'docs');
const THREE = path.join(__dirname, 'node_modules', 'three');
const TIPOS = { '.html':'text/html; charset=utf-8', '.json':'application/json', '.jpg':'image/jpeg', '.png':'image/png' };
const fallos = [];
const ok = (cond, txt) => { console.log((cond ? '  bien   ' : '  FALLA  ') + txt); if (!cond) fallos.push(txt); };

(async () => {
  const srv = http.createServer((q, r) => {
    const f = path.join(DOCS, decodeURIComponent(q.url.split('?')[0]).replace(/^\/$/, '/index.html'));
    if (!f.startsWith(DOCS) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'content-type': TIPOS[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r);
  });
  await new Promise(s => srv.listen(0, s)); const url = `http://localhost:${srv.address().port}/`;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1400, height: 860 } }); p.setDefaultTimeout(120000);
  await p.addInitScript(() => { window.__LITE = true; });
  const errores = []; p.on('pageerror', e => errores.push(e.message));
  await p.route('**/*', r => { const u = r.request().url();
    if (u.includes('three.min.js')) return r.fulfill({ path: path.join(THREE, 'build/three.min.js'), contentType: 'text/javascript' });
    if (u.includes('OrbitControls.js')) return r.fulfill({ path: path.join(THREE, 'examples/js/controls/OrbitControls.js'), contentType: 'text/javascript' });
    if (u.startsWith(url)) return r.continue();
    return r.abort(); });   // tipografías y demás recursos externos no hacen falta para la prueba
  await p.goto(url);
  await p.waitForFunction(() => document.getElementById('loading').hidden && /ha/.test(document.getElementById('stArea').textContent));
  const txt = id => p.textContent('#' + id);
  const ha = async () => { const s = (await txt('stArea')).replace(/\./g, '').replace(',', '.'); return parseFloat(s) * (/mil/.test(s) ? 1000 : 1); };

  console.log('Carga');
  ok((await txt('chipShareTxt')).includes('Modo local'), 'fuera de claude.ai entra en modo local');
  ok(/Corrida \d{4}-\d\d-\d\d/.test(await txt('wxSrc')), 'el pronóstico está cargado');
  const a0 = await ha(); ok(a0 > 0, `la proyección inicial calcula un área (${a0} ha)`);

  console.log('Escenarios');
  await p.click('[data-wx=manual]'); await p.click('[data-preset=normal]'); await p.waitForTimeout(800); const aN = await ha();
  await p.click('[data-preset=critico]'); await p.waitForTimeout(800); const aC = await ha();
  ok(aC > aN && aN > 0, `el día crítico quema más que una tarde normal (${aC} ha contra ${aN} ha)`);
  const celdas = async () => (await p.evaluate(() => window.__dbg.sim())).n;
  const nino = v => p.evaluate(v => { const e = document.getElementById('inNino'); e.checked = v; e.dispatchEvent(new Event('change', { bubbles: true })); }, v);
  await p.click('[data-preset=normal]'); await nino(false); await p.waitForTimeout(500); const c0 = await celdas();
  await nino(true); await p.waitForTimeout(500); const c1 = await celdas();
  ok(c1 > c0, `el escenario El Niño aumenta el área alcanzada (${c1} celdas contra ${c0})`);
  const r1 = await p.evaluate(() => window.__dbg.sim()), r2 = await p.evaluate(() => window.__dbg.sim());
  ok(r1.n === r2.n && r1.s === r2.s && r1.n > 0, `el cálculo es repetible (${r1.n} celdas alcanzadas)`);
  ok(r2.ms < 3000, `el cálculo tarda poco (${Math.round(r2.ms)} ms)`);

  console.log('Recursos, bitácora y exportación');
  await p.click('#tab-res'); await p.click('#btnDemo'); await p.waitForTimeout(800);
  ok(await p.locator('#resList .res').count() > 0, 'los recursos de ejemplo aparecen en la lista');
  await p.click('#tab-log'); await p.fill('#logTxt', 'Prueba automática'); await p.click('#logForm button[type=submit]'); await p.waitForTimeout(500);
  ok((await txt('logList')).includes('Prueba automática'), 'la bitácora guarda una anotación');
  await p.click('#btnKml'); await p.waitForTimeout(1500);
  ok((await p.inputValue('#expOut')).includes('<kml'), 'la exportación KML genera contenido');
  await p.click('#btnCsv'); await p.waitForTimeout(1000);
  ok((await p.inputValue('#expOut')).includes('Prueba automática'), 'la exportación CSV incluye la bitácora');

  ok(errores.length === 0, 'sin errores de programa en la página' + (errores.length ? ': ' + errores.join(' | ') : ''));
  await b.close(); srv.close();
  console.log(fallos.length ? `\n${fallos.length} comprobación(es) fallaron.` : '\nTodo bien.');
  process.exit(fallos.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
