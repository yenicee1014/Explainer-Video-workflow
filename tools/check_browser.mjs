// Optional browser checks. Run a repository HTTP server before this command.
import puppeteer from 'puppeteer-core';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const url=process.env.PREVIEW_URL||'http://127.0.0.1:3033/projects/weather-ai/';
const executablePath=process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const browser=await puppeteer.launch({executablePath,headless:true});
try {
  const page=await browser.newPage();
  const errors=[],failed=[],outOfBounds=[],samples=[],chapterChecks=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('requestfailed',r=>failed.push(new URL(r.url()).pathname));
  await page.setViewport({width:1080,height:1920,deviceScaleFactor:1});
  const response=await page.goto(`${url}?capture`,{waitUntil:'networkidle0'});
  await page.waitForFunction(()=>window.weatherPreview?.ready);
  const metadata=await page.evaluate(()=>({scenes:weatherPreview.data.scenes.length,
    chapters:weatherPreview.data.chapters.length,duration:weatherPreview.data.duration,
    audio:weatherPreview.data.audio,audioElements:document.querySelectorAll('audio').length}));
  for(let i=0;i<metadata.scenes;i++){
    const sample=await page.evaluate(i=>{
      const s=weatherPreview.data.scenes[i];weatherPreview.render(s.start+s.duration*.8);
      const boxes=[...document.querySelectorAll('#stage svg text')].map(e=>{
        const r=e.getBBox();return {text:e.textContent,x:r.x,y:r.y,w:r.width,h:r.height};
      });
      return {id:s.id,title:s.title,issues:boxes.filter(b=>b.x<0||b.y<0||b.x+b.w>1080||b.y+b.h>1920)};
    },i);
    if(sample.issues.length)outOfBounds.push(sample);
    samples.push({id:sample.id,title:sample.title});
  }
  await page.evaluate(()=>weatherPreview.render(100));const a=await page.screenshot();
  await page.evaluate(()=>{weatherPreview.render(700);weatherPreview.render(0);weatherPreview.render(100)});
  const deterministic=a.equals(await page.screenshot());
  await page.setViewport({width:1440,height:1000});
  await page.goto(url,{waitUntil:'networkidle0'});await page.waitForFunction(()=>window.weatherPreview?.ready);
  for(let i=0;i<metadata.chapters;i++){
    await page.click(`#chapters button:nth-child(${i+1})`);
    const check=await page.evaluate(i=>{
      const s=weatherPreview.data.scenes.find(s=>s.chapter===i+1);
      return {chapter:i+1,ok:weatherPreview.state.time===s.start&&weatherPreview.data.scenes[weatherPreview.state.scene].id===s.id&&document.querySelectorAll('#chapters .active').length===1};
    },i);chapterChecks.push(check);
  }
  await page.click('#chapters button:first-child');await page.click('#play');
  await page.waitForFunction(()=>weatherPreview.state.time>1,{timeout:10000});
  await page.click('#play');const paused=await page.evaluate(()=>weatherPreview.state);
  await page.evaluate(()=>new Promise(r=>setTimeout(r,120)));
  const pauseStable=await page.evaluate(time=>weatherPreview.state.time===time&&!weatherPreview.state.playing,paused.time);
  await page.evaluate(()=>weatherPreview.seek(weatherPreview.data.duration-.2));await page.click('#play');
  await page.waitForFunction(()=>!weatherPreview.state.playing,{timeout:10000});
  const ended=await page.evaluate(()=>weatherPreview.state.time===weatherPreview.data.duration);
  await page.evaluate(()=>weatherPreview.seek(5));
  await fs.mkdir(path.join(ROOT,'reports'),{recursive:true});
  await page.screenshot({path:path.join(ROOT,'reports/player.png')});
  const report={status:'passed',http:response.status(),...metadata,errors,failed,
    out_of_bounds:outOfBounds,deterministic,chapters_count:metadata.chapters,chapters_playback:chapterChecks,pauseStable,ended,samples,
    scope:'Silent browser structure, SVG text bounds, deterministic seeking, chapter controls, start/pause/end only; not expert scientific or full human visual review'};
  const ok=response.status()===200&&metadata.scenes===40&&metadata.audio===false&&metadata.audioElements===0&&
    !errors.length&&!failed.length&&!outOfBounds.length&&deterministic&&chapterChecks.every(c=>c.ok)&&pauseStable&&ended;
  report.status=ok?'passed':'failed';
  await fs.writeFile(path.join(ROOT,'reports/browser-check.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));if(!ok)process.exitCode=1;
} finally {await browser.close();}
