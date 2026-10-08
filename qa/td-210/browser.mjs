import {createRequire} from 'node:module';
import {mkdir,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {createGameServer} from '../../../harness/webgl/server.mjs';
const {chromium}=createRequire(new URL('../../../harness/webgl/package.json',import.meta.url))('playwright');
const [webroot,out,phase='before',source='unrecorded']=process.argv.slice(2);
await mkdir(out,{recursive:true});
const result={phase,source,errors:[],shots:[],physical_phone:false};
const logs=[];
const server=await createGameServer(resolve(webroot));
await new Promise(r=>server.listen(0,'127.0.0.1',r));
let browser;
try {
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  result.browser=browser.version();
  const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1,hasTouch:true});
  page.on('console',m=>{logs.push(m.text());if(/ERROR:|SCRIPT ERROR:|Parse Error:|Failed loading resource/.test(m.text()))result.errors.push(m.text());});
  page.on('pageerror',e=>result.errors.push(e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/capture.html?kind=routes&phase=${phase}&source=${source}`,{waitUntil:'domcontentloaded'});
  let last=0,progress=Date.now();
  const deadline=Date.now()+3600000;
  while(Date.now()<deadline) {
    const state=await page.evaluate(()=>({command:window.__td210Command,result:window.__td210Result}));
    if(state.result){result.capture=state.result;break;}
    const c=state.command;
    if(c&&c.id!==last){
      last=c.id;progress=Date.now();
      if(c.action==='viewport')await page.setViewportSize({width:c.size[0],height:c.size[1]});
      if(c.action==='shot'){
        const file=resolve(out,c.file);await mkdir(dirname(file),{recursive:true});
        await writeFile(file,Buffer.from(c.png,'base64'));result.shots.push(c.file);
        console.log('TD210_WEB_SHOT',result.shots.length,c.file);
      }
      await page.evaluate(id=>window.__td210Ack=id,c.id);
    }
    if(Date.now()-progress>240000)throw Error('No capture progress for 240 seconds');
    await page.waitForTimeout(30);
  }
  if(!result.capture)throw Error('Capture deadline exceeded');
} catch(e){result.errors.push(String(e));}
finally {
  await browser?.close();server.closeAllConnections();await new Promise(r=>server.close(r));
  await writeFile(resolve(out,'raw-console.log'),logs.join('\n'));
  await writeFile(resolve(out,'result.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify({shots:result.shots.length,errors:result.errors.length,complete:!!result.capture}));
  if(!result.capture)process.exitCode=1;
}
