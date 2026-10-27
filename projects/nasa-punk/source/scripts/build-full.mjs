import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {spawnSync} from "node:child_process";
import {makeScenes} from "./rebuild-scenes.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const data = JSON.parse(await fs.readFile(path.join(root,"rebuild-timeline.json"),"utf8"));
const logoSource = await fs.readFile(path.join(root,"assets/images/nasa.svg"),"utf8");
const logo = logoSource.match(/<path d="([^"]+)"/)?.[1];
if (!logo) throw new Error("Required NASA wordmark missing");
const esc = text => text.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll('"',"&quot;");
const sampleOnly = process.argv.includes("--sample-only");
const scenes = makeScenes({...data,chapters:sampleOnly?[data.chapters[1]]:data.chapters},logo);
await fs.mkdir(path.join(root,"compositions"),{recursive:true});
for (const scene of scenes) {
  const html = `<!doctype html><html><body><template>
<style>
@font-face{font-family:Archivo;src:url("../assets/fonts/Archivo.ttf");font-weight:100 900}
@font-face{font-family:SpaceMono;src:url("../assets/fonts/SpaceMono-Regular.ttf");font-weight:400}
@font-face{font-family:NotoSC;src:url("../assets/fonts/NotoSansSC-Regular.woff");font-weight:400}
@font-face{font-family:NotoSC;src:url("../assets/fonts/NotoSansSC-Bold.woff");font-weight:700}
#${scene.id}{position:absolute;inset:0;overflow:hidden}#${scene.id} svg.scene{width:100%;height:100%;display:block}#${scene.id} .latent{opacity:0}#${scene.id} .paper-shadow{filter:drop-shadow(5px 8px 6px #0005)}#${scene.id} text{font-family:Archivo,NotoSC,sans-serif;letter-spacing:0}#${scene.id} .mono{font-family:SpaceMono,NotoSC,monospace}#${scene.id} .cn{font-family:NotoSC,sans-serif}</style>
<div id="${scene.id}" data-composition-id="${scene.id}" data-width="1280" data-height="720" data-duration="${scene.chapter.duration}">
<svg class="scene" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">${scene.body}</svg></div>
<script>(()=>{const tl=gsap.timeline({paused:true});const prefix=${JSON.stringify(scene.id)};
const q=name=>'#'+prefix+'-'+name;
const A=${JSON.stringify(Object.fromEntries(scene.chapter.lines.map(l=>[l.id,l.localStart+l.onset])))};
const R=(name,time,duration=.55)=>tl.fromTo(q(name),{opacity:0,y:12},{opacity:1,y:0,duration,ease:'power2.out',immediateRender:false},time);
const F=(name,time,duration=.4)=>tl.to(q(name),{opacity:0,duration,ease:'power1.inOut'},time);
const D=(name,time,duration=.7)=>tl.fromTo(q(name),{attr:{'stroke-dashoffset':1}},{attr:{'stroke-dashoffset':0},duration,ease:'power1.inOut',immediateRender:false},time);
${scene.motion}
window.__timelines[${JSON.stringify(scene.id)}]=tl;})();</script>
</template></body></html>`;
  await fs.writeFile(path.join(root,`compositions/${scene.chapter.id}.html`),html);
  await fs.rm(path.join(root,`compositions/${scene.chapter.id}.motion.json`),{force:true});
  await fs.writeFile(path.join(root,`compositions/${scene.chapter.id}.beats.json`),
    JSON.stringify({version:1,compositionId:scene.id,duration:scene.chapter.duration,
      narrativeAnchors:scene.chapter.lines.map(l=>({id:l.id,time:l.localStart+l.onset,text:l.text})),
      authoredActions:scene.actions},null,2));
}
function assemble(chapters, sample=false) {
  const offset = chapters[0].start;
  const duration = chapters.at(-1).end-offset;
  const compId = sample ? "nasa-semantic-sample" : "nasa-punk-full";
  const hosts = chapters.map(ch => `<div id="host-${ch.id}" class="clip scene-host" data-composition-id="nasa-${ch.id}" data-composition-src="compositions/${ch.id}.html" data-start="${(ch.start-offset).toFixed(6)}" data-duration="${ch.duration}" data-track-index="1" data-width="1280" data-height="720"></div>`).join("\n");
  const captions = chapters.flatMap(ch => ch.lines).map((line,index) =>
    `<div id="${compId}-caption-${index}" class="clip caption" data-start="${(line.start-offset).toFixed(6)}" data-duration="${line.duration.toFixed(6)}" data-track-index="20"><span class="caption-stripe"></span><span>${esc(line.text)}</span></div>`).join("\n");
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>NASA 朋克 | 代码重建</title>
<script src="assets/vendor/gsap.min.js"></script><style>
@font-face{font-family:Archivo;src:url("assets/fonts/Archivo.ttf");font-weight:100 900}
@font-face{font-family:SpaceMono;src:url("assets/fonts/SpaceMono-Regular.ttf");font-weight:400}
@font-face{font-family:NotoSC;src:url("assets/fonts/NotoSansSC-Regular.woff");font-weight:400}
@font-face{font-family:NotoSC;src:url("assets/fonts/NotoSansSC-Bold.woff");font-weight:700}
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#1c1b17}
#root{width:100%;height:100%;position:relative;overflow:hidden}
.scene-host{position:absolute;inset:0}
.caption{position:absolute;inset:auto 90px 25px;z-index:1000;margin:0 auto;width:fit-content;max-width:1100px;min-height:42px;display:flex;align-items:center;gap:15px;padding:7px 16px 8px 0;background:#22221fed;color:#f5f2e9;font:22px/1.45 NotoSC,sans-serif;text-align:center}
.caption-stripe{width:12px;min-width:12px;align-self:stretch;background:linear-gradient(90deg,#4c5a68 0 25%,#7a7f4e 25% 50%,#d2a85e 50% 75%,#a8432f 75%)}
</style></head><body><div id="root" data-composition-id="${compId}" data-width="1280" data-height="720" data-fps="30" data-duration="${duration}">
${hosts}${captions}
<audio id="${compId}-audio" class="clip" src="assets/rebuild-mix.m4a" data-start="0" data-media-start="${offset}" data-duration="${duration}" data-track-index="10" data-volume="1"></audio>
</div><script>(()=>{const tl=gsap.timeline({paused:true});window.__timelines[${JSON.stringify(compId)}]=tl;})();</script></body></html>`;
}
const allSource = scenes.map(s=>s.body).join("\n")+JSON.stringify(data);
const characterFile = path.join(root,".hyperframes/rebuild-characters.txt");
await fs.mkdir(path.dirname(characterFile),{recursive:true});
await fs.writeFile(characterFile,allSource);
for (const weight of ["Regular","Bold"]) {
  const result = spawnSync("python3",["-m","fontTools.subset",
    path.join(root,`assets/fonts/NotoSansSC-${weight}.otf`),
    `--text-file=${characterFile}`,"--flavor=woff",
    `--output-file=${path.join(root,`assets/fonts/NotoSansSC-${weight}.woff`)}`],{encoding:"utf8"});
  if (result.status !== 0) throw new Error(result.stderr);
}
await fs.writeFile(path.join(root,"index.html"),sampleOnly?assemble([data.chapters[1]],true):assemble(data.chapters));
await fs.rm(path.join(root,"semantic-sample.html"),{force:true});
const wordmark = data.chapters[1];
const motionOffset = sampleOnly ? 0 : wordmark.start;
await fs.writeFile(path.join(root,"index.motion.json"),JSON.stringify({version:1,
  duration:sampleOnly?wordmark.duration:data.duration,
  assertions:[
    {kind:"appearsBy",selector:"#nasa-wordmark-word",bySec:motionOffset+wordmark.lines.find(l=>l.id==="stroke").localStart+1},
    {kind:"before",a:"#nasa-wordmark-word",b:"#nasa-wordmark-rockets"},
    {kind:"before",a:"#nasa-wordmark-rockets",b:"#nasa-wordmark-wormlabel"},
    {kind:"staysInFrame",selector:"#nasa-wordmark-word"}
  ]},null,2));
const time = t => {
  const ms=Math.round(t*1000);
  return `${String(Math.floor(ms/3600000)).padStart(2,"0")}:${String(Math.floor(ms/60000)%60).padStart(2,"0")}:${String(Math.floor(ms/1000)%60).padStart(2,"0")},${String(ms%1000).padStart(3,"0")}`;
};
await fs.mkdir(path.join(root,"renders"),{recursive:true});
const lines=data.chapters.flatMap(ch=>ch.lines);
await fs.writeFile(path.join(root,"renders/nasa-punk-rebuild.srt"),lines.map((l,i)=>`${i+1}\n${time(l.start)} --> ${time(l.start+l.duration)}\n${l.text}\n`).join("\n"));
await fs.writeFile(path.join(root,"STORYBOARD.md"),`# NASA 朋克代码重建\n\n原片镜头语法参考；重新撰写及合成旁白。时间来自独立录音实测。\n\n`+
  scenes.map((s,i)=>`## Frame ${i+1}\n\nstatus: authored\nsrc: compositions/${s.chapter.id}.html\nstart: ${s.chapter.start.toFixed(3)}\nduration: ${s.chapter.duration.toFixed(3)}\nshape: persistent-objects / draw-on / semantic-reveal / camera-reframe\n\n${s.actions.join("\n\n")}\n`).join("\n"));
console.log(`Built ${scenes.length} independent scene compositions, ${lines.length} recorded caption phrases, ${data.duration.toFixed(3)}s.`);
