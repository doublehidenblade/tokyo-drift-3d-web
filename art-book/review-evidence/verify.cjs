const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs=require('fs');
const path=require('path');
const {execFileSync}=require('child_process');
const out=__dirname;
const baseline=execFileSync('git',['show','2e8c63e3030247fc90e0eea273867181bd5d1098:art-book/index.html'],{encoding:'utf8'});
const url=process.env.ARTBOOK_URL || 'http://127.0.0.1:8765/art-book/';
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 let results=[];
 const targets=[['cover',null],['loop','9A. THE WORKING SHIFT'],['economy','Local production — recommended'],['ticks','Tick, job and transaction'],['garage','B6. HOME GARAGE'],['research','Direct-reference comparison'],['roadmap','Roadmap: reuse'],['tests','Proposed playtest gates'],['provenance','Change summary and provenance']];
 for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]){
  const p=await b.newPage({viewport:{width,height}});const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.route('**/art-book/',r=>r.fulfill({contentType:'text/html',body:baseline}));
  await p.goto(url,{waitUntil:'networkidle'});
  await p.screenshot({path:`${out}/before-${name}.png`});
  await p.unroute('**/art-book/');await p.reload({waitUntil:'networkidle'});
  for(const [label,heading] of targets){
   if(heading)await p.getByRole('heading').filter({hasText:heading}).first().evaluate(e=>e.scrollIntoView());else await p.evaluate(()=>scrollTo(0,0));
   await p.screenshot({path:`${out}/after-${name}-${label}.png`});
  }
  for(const [label,text] of [['source-pair','Source pair (2026-10-06 draft):'],['source-resolution','Source resolution, 2026-10-06:']]){
   await p.locator('p').filter({hasText:text}).first().evaluate(e=>e.scrollIntoView());
   await p.screenshot({path:`${out}/after-${name}-${label}.png`});
  }
  const audit=await p.evaluate(()=>{
   const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
   return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,duplicateIds:ids.filter((id,i)=>ids.indexOf(id)!==i),brokenAnchors:[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href')).filter(a=>!document.getElementById(a.slice(1))),images:[...document.images].map(i=>i.getAttribute('src')),localLinks:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).filter(a=>!a.startsWith('#')&&!a.startsWith('http')),tablesOutsideScroll:[...document.querySelectorAll('table')].filter(t=>t.scrollWidth>innerWidth&&t.parentElement.className!=='twrap').length};
  });
  // Lazy images must be requested independently to verify every file, even below viewport.
  const brokenFiles=[];
  for(const f of new Set([...audit.images,...audit.localLinks])){const response=await p.request.get(new URL(f,p.url()).href);if(!response.ok())brokenFiles.push({f,status:response.status()});}
  results.push({viewport:name,...audit,images:audit.images.length,errors,brokenFiles});await p.close();
 }
 fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify(results,null,2));
 for(const r of results)if(r.scrollWidth>r.width||r.duplicateIds.length||r.brokenAnchors.length||r.brokenFiles.length||r.errors.length)throw new Error('Browser audit failed: '+JSON.stringify(r));console.log(JSON.stringify(results,null,2));await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
