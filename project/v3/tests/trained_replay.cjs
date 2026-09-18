const {chromium}=require(process.env.PLAYWRIGHT_MODULE),fs=require('fs'),path=require('path');
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH,args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{const page=await browser.newPage({viewport:{width:1440,height:1180}}),errors=[],checks=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto((process.env.APP_URL||'http://127.0.0.1:8877/')+'viewer/?variant=trained',{waitUntil:'networkidle'});await page.waitForFunction(()=>window.flyPiano?.state.ready);
for(const key of ['merry','pool']){await page.evaluate(async k=>{await flyPiano.load(k,'trained');flyPiano.seek(flyPiano.score.duration-.1)},key);checks.push(await page.evaluate(()=>({song:flyPiano.state.song,variant:flyPiano.state.variant,duration:flyPiano.replay.duration,last:document.querySelector('#measure').textContent,run:flyPiano.replay.run_id})));}
await page.evaluate(()=>flyPiano.seek(42));await page.screenshot({path:path.resolve(__dirname,'../paper/figures/viewer.jpg'),type:'jpeg',quality:88,fullPage:true});
if(errors.length)throw Error(errors.join('\n'));fs.writeFileSync(path.resolve(__dirname,'../qa/trained_ui_check.json'),JSON.stringify({checks,errors},null,2));console.log(JSON.stringify(checks));
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
