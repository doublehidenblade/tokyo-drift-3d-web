// Verify the unmodified shipping entry (menu -> L -> live Lower City), separately
// from the parked diagnostic capture scene. No production hook or state injection.
import {createRequire} from 'node:module';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {createGameServer} from '../../../harness/webgl/server.mjs';
const {chromium}=createRequire(new URL('../../../harness/webgl/package.json',import.meta.url))('playwright');
const [webroot,out]=process.argv.slice(2);
await mkdir(out,{recursive:true});
const result={status:'failed',scope:'Ordinary exported menu and Lower City; real keyboard input; software renderer; no device FPS claim.',errors:[],screenshots:[]};
result.pack_sha256=createHash('sha256').update(await readFile(resolve(webroot,'index.pck'))).digest('hex');
const logs=[];const server=await createGameServer(resolve(webroot));
await new Promise(r=>server.listen(0,'127.0.0.1',r));
let browser;let phase='menu';
try {
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 result.browser=browser.version();
 const page=await browser.newPage({viewport:{width:1280,height:720},hasTouch:true,deviceScaleFactor:1});
 page.on('console',m=>{logs.push(`[${phase}] ${m.text()}`);if(/SCRIPT ERROR:|Parse Error:|Failed loading resource|ERROR:/.test(m.text()))result.errors.push({phase,message:m.text()});});
 page.on('pageerror',e=>result.errors.push({phase,message:e.message}));
 const started=Date.now();
 await page.goto(`http://127.0.0.1:${server.address().port}/`,{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>window.__tdPrepared===true,null,{timeout:240000});
 result.menu_ready_ms=Date.now()-started;
 await page.screenshot({path:resolve(out,'ordinary-menu.png'),timeout:120000});result.screenshots.push('ordinary-menu.png');
 phase='lower-city';const entered=Date.now();
 await page.keyboard.press('KeyL');
 await page.waitForFunction(()=>window.__lowerCityReady===true,null,{timeout:240000});
 result.lower_city_ready_ms=Date.now()-entered;
 await page.waitForFunction(()=>window.__lowerCityState?.rects?.map,null,{timeout:60000});
 result.initial_state=await page.evaluate(()=>window.__lowerCityState);
 await page.screenshot({path:resolve(out,'ordinary-hud-1280.png'),timeout:120000});result.screenshots.push('ordinary-hud-1280.png');
 await page.setViewportSize({width:844,height:390});await page.waitForTimeout(2000);
 await page.screenshot({path:resolve(out,'ordinary-hud-844.png'),timeout:120000});result.screenshots.push('ordinary-hud-844.png');
 await page.keyboard.down('ArrowUp');
 try {await page.waitForFunction(()=>window.__lowerCityState?.speed>3,null,{timeout:30000});}
 finally {result.driving_state=await page.evaluate(()=>window.__lowerCityState);await page.keyboard.up('ArrowUp');}
 if(result.errors.length)throw Error('Console errors were recorded; inspect raw-console.log');
 result.status='passed';
} catch(e){result.errors.push({phase,message:String(e)});process.exitCode=1;}
finally {
 await browser?.close();server.closeAllConnections();await new Promise(r=>server.close(r));
 await writeFile(resolve(out,'raw-console.log'),logs.join('\n')+'\n');
 await writeFile(resolve(out,'result.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result));
}
