const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{
  const b = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const html = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"></head><style>[hidden]{display:none!important}</style><body style="margin:0;font:14px system-ui">'+fs.readFileSync('/home/user/lumaco/app/lumaco-fuego-3d.html','utf8')+'</body></html>';
  const run = async (name,w,h,scheme,actions)=>{
    const p = await b.newPage({viewport:{width:w,height:h},colorScheme:scheme}); if(name!=='hi') await p.addInitScript(()=>{window.__LITE=true;}); p.setDefaultTimeout(180000);
    p.on('console',m=>{ if(m.type()==='error'||m.type()==='warning') console.log(name,'console',m.type(),m.text().slice(0,300)); });
    p.on('pageerror',e=>console.log(name,'PAGEERROR',e.message));
    await p.route('**/*',r=>{ const u=r.request().url();
      if(u.includes('three.min.js')) return r.fulfill({path:'node_modules/three/build/three.min.js',contentType:'text/javascript'});
      if(u.includes('OrbitControls.js')) return r.fulfill({path:'node_modules/three/examples/js/controls/OrbitControls.js',contentType:'text/javascript'});
      if(/\.(jpg|png)$/.test(u)) return r.fulfill({path:'/home/user/lumaco/pub/'+u.split('/').pop()});
      if(u.startsWith('http://x.test/')) return r.fulfill({body:html,contentType:'text/html'});
      return r.abort(); });
    await p.goto('http://x.test/'); await p.waitForTimeout(name==='phone'?5000:14000);
    if(actions) await actions(p);
    await p.screenshot({path:`/home/user/lumaco/test/${name}.png`,fullPage:false}); await p.close();
  };
  const which=process.argv[2]||'all';
  if(which==='hi') await run('hi',1400,860,'light',async p=>{ await p.waitForTimeout(20000); await p.click('[data-wx=manual]'); await p.click('[data-preset=critico]'); await p.evaluate(()=>{const e=document.getElementById('inTime'); e.value=7; e.dispatchEvent(new Event('input'));}); await p.click('#zIn'); await p.click('#zIn'); await p.waitForTimeout(15000); console.log(await p.evaluate(()=>document.getElementById('stArea').textContent)); });
  if(which==='all'||which==='d') await run('desk',1400,860,'dark',async p=>{ await p.click('#dirPad [data-dir="135"]'); await p.waitForTimeout(1500); console.log(await p.evaluate(()=>[document.getElementById('sumH').textContent,document.getElementById('sumS').textContent,document.getElementById('sumN').textContent,document.getElementById('dirNote').textContent].join(' | '))); });
  if(which==='all'||which==='l') await run('light',1400,860,'light',async p=>{ await p.click('[data-preset=puelche]'); await p.click('#tab-res'); await p.click('#btnDemo'); await p.waitForTimeout(800); const info=await p.evaluate(()=>[document.getElementById('stArea').textContent,document.getElementById('stRos').textContent,document.getElementById('stEta').innerText]); console.log(JSON.stringify(info)); });
  if(which==='all'||which==='w') await run('wx',1400,860,'light',async p=>{ console.log(await p.evaluate(()=>[document.getElementById('wxBox').innerText.slice(0,200),document.getElementById('wxSrc').textContent,document.getElementById('stArea').textContent,document.getElementById('clockSub').textContent,document.getElementById('inDay').options.length].join(' || '))); await p.selectOption('#inDay',{index:2}); await p.waitForTimeout(700); console.log(await p.evaluate(()=>document.getElementById('stArea').textContent+' '+document.getElementById('inHour').selectedOptions[0].textContent+' '+document.getElementById('clockSub').textContent)); });
  if(which==='all'||which==='z') await run('zoom',1400,860,'light',async p=>{ await p.click('#tab-cap'); await p.fill('#inLoc','Lumaco'); await p.dispatchEvent('#inLoc','change'); await p.waitForTimeout(1500); console.log(await p.evaluate(()=>document.getElementById('locInfo').textContent)); });
  if(which==='all'||which==='m') await run('phone',400,800,'dark',async p=>{ await p.click('#btnIgnite'); await p.mouse.click(150,330); await p.waitForTimeout(600); await p.click('#btnPlay'); await p.waitForTimeout(2500); console.log(await p.evaluate(()=>document.getElementById('igniteInfo').textContent+' | sw='+document.documentElement.scrollWidth)); });
  if(which==='n') await run('new',1400,860,'light',async p=>{
    await p.click('#tab-res'); await p.click('#btnDemo'); await p.waitForTimeout(1200); await p.screenshot({path:'/home/user/lumaco/test/res.png'});
    await p.click('#tab-sim'); await p.click('#btnPerim'); for (const [x,y] of [[640,420],[720,410],[740,480],[660,500]]){ await p.mouse.click(x,y); await p.waitForTimeout(300); }
    console.log(await p.evaluate(()=>document.getElementById('hintTxt').textContent)); await p.click('#hintDone'); await p.waitForTimeout(2500);
    await p.evaluate(()=>{const e=document.getElementById('inTime'); e.value=12; e.dispatchEvent(new Event('input'));}); await p.waitForTimeout(800);
    console.log(await p.evaluate(()=>[document.getElementById('igniteInfo').textContent,document.getElementById('sumS').textContent,'cut:'+document.getElementById('stCut').innerText.replace(/\n/g,',').slice(0,300),document.getElementById('wxBox').innerText.slice(0,330),document.getElementById('worstTxt').textContent].join(' || ')));
    await p.screenshot({path:'/home/user/lumaco/test/perim.png'});
    await p.click('#inWorst'); await p.waitForTimeout(1500); console.log('worst', await p.evaluate(()=>document.getElementById('sumS').textContent));
    await p.click('#tab-log'); await p.fill('#logTxt','Brigada llega al sector norte'); await p.click('#logForm button'); await p.waitForTimeout(300);
    await p.click('#btnCsv'); await p.waitForTimeout(300); console.log('CSV', JSON.stringify(await p.evaluate(()=>document.getElementById('expOut').value)), await p.evaluate(()=>document.getElementById('expNote').textContent));
    await p.click('#btnKml'); await p.waitForTimeout(1500); const kml=await p.evaluate(()=>document.getElementById('expOut').value); fs.writeFileSync('/home/user/lumaco/test/out.kml',kml); console.log('KML',kml.length);
  });
  if(which==='c') await run('cut',1400,860,'dark',async p=>{ await p.click('[data-wx=manual]'); await p.click('[data-preset=critico]'); await p.evaluate(()=>{const e=document.getElementById('inH'); e.value=24; e.dispatchEvent(new Event('input'));}); await p.waitForTimeout(3000);
    console.log(JSON.stringify(await p.evaluate(()=>[__dbg.exits(),__dbg.locs(),__dbg.base(),[2,4,8,10,12,14,16,18,20,22].map(h=>h+":"+__dbg.at(h*60).cut.join("+"))])));
    for (const t of [24]){ await p.evaluate(t=>{const e=document.getElementById('inTime'); e.value=t; e.dispatchEvent(new Event('input'));},t); await p.waitForTimeout(600); console.log(t, await p.evaluate(()=>document.getElementById('sumS').textContent+' || '+document.getElementById('stCut').innerText.replace(/\n/g,',').slice(0,400))); } });
  await b.close();
})();
