import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {spawnSync} from "node:child_process";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const script = JSON.parse(await fs.readFile(path.join(root, "rebuild-script.json"), "utf8"));
const folder = path.join(root, "assets/rebuild-voice");
await fs.mkdir(folder, {recursive:true});
const run = (cmd, args) => {
  const result = spawnSync(cmd, args, {encoding:"utf8", timeout:60000});
  if (result.status !== 0) throw new Error(result.stderr || `${cmd} failed`);
  return result;
};
const probe = filename => Number(run("ffprobe", ["-v","error","-show_entries",
  "format=duration","-of","csv=p=0",filename]).stdout.trim());
let cursor = 0;
const chapters = [];
for (const chapter of script.chapters) {
  const lines = [];
  let local = .65;
  for (const line of chapter.lines) {
    const id = `${chapter.id}-${line.id}`;
    const filename = path.join(folder, `${id}.wav`);
    const cache = path.join(folder, `${id}.json`);
    let info;
    try {
      info = JSON.parse(await fs.readFile(cache, "utf8"));
      if (info.text !== line.text || info.rate !== script.rate) throw new Error("Changed text");
      await fs.access(filename);
    } catch {
      const source = path.join(folder, `${id}.aiff`);
      run("say", ["-v",script.voice,"-r",String(script.rate),"-o",source,line.text]);
      const sourceDuration = probe(source);
      const detection = run("ffmpeg",["-hide_banner","-i",source,"-af",
        "silencedetect=noise=-45dB:d=0.08","-f","null","-"]).stderr;
      const events = [...detection.matchAll(/silence_(start|end): ([\d.]+)/g)]
        .map(m => ({type:m[1],time:Number(m[2])}));
      const onset = events[0]?.type === "start" && events[0].time < .1 ?
        (events.find(e=>e.type === "end")?.time ?? 0) : 0;
      const last = events.at(-1);
      const tail = last?.type === "end" && Math.abs(last.time-sourceDuration)<.1 ?
        ([...events].reverse().find(e=>e.type === "start")?.time ?? sourceDuration) : sourceDuration;
      const trimStart = Math.max(0,onset-.04);
      const trimEnd = Math.min(sourceDuration,tail+.1);
      run("ffmpeg",["-y","-v","error","-i",source,"-af",
        `atrim=start=${trimStart}:end=${trimEnd},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=${Math.max(.1,trimEnd-trimStart-.02)}:d=0.02`,
        "-ac","1","-ar","48000",filename]);
      info = {text:line.text,rate:script.rate,duration:probe(filename),
        onset:Math.max(0,onset-trimStart),trimStart,trimEnd,sourceDuration};
      await fs.writeFile(cache,JSON.stringify(info,null,2));
    }
    lines.push({...line,...info,key:id,path:`assets/rebuild-voice/${id}.wav`,
      localStart:local,start:cursor+local,anchor:cursor+local+info.onset});
    local += info.duration + .38;
    console.log(`${id}: ${info.duration.toFixed(2)}s @ ${cursor.toFixed(2)} + ${lines.at(-1).localStart.toFixed(2)}`);
  }
  const duration = Math.ceil(Math.max(chapter.minimum,local+.6)*30)/30;
  chapters.push({...chapter,start:cursor,end:cursor+duration,duration,lines});
  cursor += duration;
}
const timeline = {duration:cursor,fps:30,width:1280,height:720,
  voice:script.voice,rate:script.rate,originalAudio:false,
  alignment:"individually recorded sentence boundaries, waveform silence trimmed; no inferred word timestamps",
  chapters};
await fs.writeFile(path.join(root,"rebuild-timeline.json"),JSON.stringify(timeline,null,2));
console.log(`Measured narration timeline: ${cursor.toFixed(3)} seconds.`);
