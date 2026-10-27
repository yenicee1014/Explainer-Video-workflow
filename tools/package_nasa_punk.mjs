import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
if (process.argv.length !== 3) throw new Error("Usage: node tools/package_nasa_punk.mjs <local-production-project>");
const production = fs.realpathSync(process.argv[2]);
const project = path.join(root, "projects/nasa-punk");
const source = path.join(project, "source");
const verification = path.join(project, "verification");
const videoName = "video/nasa-punk-full-rebuild.mp4";
const video = path.join(root, videoName);
const read = (name) => JSON.parse(fs.readFileSync(path.join(production, name), "utf8"));
const write = (filename, value) => {
  fs.mkdirSync(path.dirname(filename), { recursive: true });
  fs.writeFileSync(filename, JSON.stringify(value, null, 2) + "\n");
};
const digest = (filename) => crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
const copy = (from, to) => {
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(path.join(production, from), to);
};
function run(command, args) {
  const result = spawnSync(command, args, { encoding: "utf8", maxBuffer: 8 * 1024 * 1024 });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`${command}: ${result.stderr}`);
  return result.stdout;
}
function sanitize(value) {
  if (typeof value === "string") {
    return value.replaceAll(production + "/", "").replaceAll(production, "[production-project]");
  }
  if (Array.isArray(value)) return value.map(sanitize);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, sanitize(item)]));
  }
  return value;
}

const snapshot = [
  "rebuild-script.json", "rebuild-timeline.json", "STORYBOARD.md",
  "package.json", "hyperframes.json", "index.html", "index.motion.json",
  "scripts/rebuild-scenes.mjs", "scripts/build-full.mjs", "scripts/prepare-rebuild-audio.mjs",
  "scripts/prepare-rebuild-assets.py", "scripts/mix-rebuild.py", "scripts/hyperframes.mjs",
  "assets/rebuild/provenance.json", "assets/sources.json",
  "assets/licenses/Archivo-OFL.txt", "assets/licenses/SpaceMono-OFL.txt", "assets/licenses/NotoSansSC-OFL.txt",
  ...fs.readdirSync(path.join(production, "compositions"))
    .filter((name) => /^[a-z-]+\.(?:html|beats\.json)$/.test(name))
    .map((name) => "compositions/" + name),
];
for (const filename of snapshot) {
  const contents = fs.readFileSync(path.join(production, filename), "utf8");
  if (/\/(?:Users|Volumes|home)\//.test(contents)) throw new Error(`Private absolute path in ${filename}`);
  copy(filename, path.join(source, filename));
}
copy("renders/nasa-punk-full-rebuild.mp4", video);
copy("renders/nasa-punk-rebuild.srt", path.join(project, "captions.srt"));
copy("renders/output-review/contact-sheet.jpg", path.join(project, "contact-sheet.jpg"));
const srt = fs.readFileSync(path.join(project, "captions.srt"), "utf8").replaceAll("\r\n", "\n");
const cues = srt.trim().split(/\n\s*\n/).map((block) => {
  const [id, times, ...text] = block.split("\n");
  if (!/^\d+$/.test(id) || !/^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$/.test(times)) {
    throw new Error("Invalid SRT cue");
  }
  return [id, times.replaceAll(",", "."), ...text].join("\n");
});
fs.writeFileSync(path.join(project, "captions.vtt"), "WEBVTT\n\n" + cues.join("\n\n") + "\n");

for (const name of ["final-check.json", "audio-sync-check.json", "full-media-probe.json"]) {
  const report = sanitize(read("renders/" + name));
  report.publication_note = "Production-stage report; only local absolute paths were sanitized. Not a full human semantic review.";
  write(path.join(verification, name), report);
}
const check = read("renders/final-check.json");
const status = sanitize(read("STATUS.json"));
status.validation.craft_warning_count = check.craft.warningCount;
status.validation.craft_warning_codes = check.craft.findings.reduce((counts, finding) => {
  counts[finding.code] = (counts[finding.code] ?? 0) + 1;
  return counts;
}, {});
status.publication_note = "Local production status with craft warning counts added from final-check.json. Individual chapters marked validated do not mean full human semantic approval. Excluded artifacts remain local and are not part of this archive.";
write(path.join(verification, "production-status.json"), status);

const probe = JSON.parse(run("ffprobe", ["-v", "error", "-show_format", "-show_streams", "-of", "json", video]));
const v = probe.streams.find((stream) => stream.codec_type === "video");
const a = probe.streams.find((stream) => stream.codec_type === "audio");
const timeline = read("rebuild-timeline.json");
run("ffmpeg", ["-y", "-v", "error", "-ss", "335", "-i", video, "-frames:v", "1", "-q:v", "2", path.join(project, "poster.jpg")]);
write(path.join(project, "delivery-manifest.json"), {
  project: "NASA-punk code rebuild",
  publication_date: "2026-10-27",
  version_scope: "Reauthored code rebuild, not a frame-for-frame replica or original creator project",
  reference: "https://www.bilibili.com/video/BV1Tsps6kE6z/",
  reference_creator: "路北路陈",
  video: {
    path: videoName, size_bytes: fs.statSync(video).size, sha256: digest(video),
    duration_seconds: Number(probe.format.duration),
    video_codec: v.codec_name, width: v.width, height: v.height,
    frame_rate: v.r_frame_rate, frame_count: Number(v.nb_frames),
    audio_codec: a.codec_name, audio_sample_rate_hz: Number(a.sample_rate), audio_channels: a.channels,
    voice: "macOS Tingting", original_soundtrack_used: false,
  },
  scene_count: timeline.chapters.length,
  narration_sentence_count: timeline.chapters.reduce((count, chapter) => count + chapter.lines.length, 0),
  chapters: timeline.chapters.map(({ id, title, start, duration }) => ({ id, title, start_seconds: start, duration_seconds: duration })),
  companions: ["captions.srt", "captions.vtt", "contact-sheet.jpg", "poster.jpg"].map((filename) => ({
    path: "projects/nasa-punk/" + filename,
    size_bytes: fs.statSync(path.join(project, filename)).size,
    sha256: digest(path.join(project, filename)),
  })),
  source_snapshot: {
    self_contained: false,
    inventory: "projects/nasa-punk/source/snapshot-manifest.json",
    omitted: ["Reference video and still-image package", "Fonts and GSAP binary", "Individual voice clips and mix cache", "Node/Python dependencies and render cache"],
  },
  review: {
    production_check_ok: check.ok,
    craft_warning_count: check.craft.warningCount,
    full_speed_human_audio_visual_review: false,
    word_by_word_human_proofread: false,
    word_level_alignment: false,
    redistribution_rights_individually_cleared: false,
  },
});
write(path.join(source, "snapshot-manifest.json"), {
  description: "Byte-for-byte production source snapshot. README and this inventory are publication additions; excluded resources are not provided.",
  self_contained: false,
  files: snapshot.map((filename) => ({ path: filename, sha256: digest(path.join(source, filename)) })),
});
console.log(JSON.stringify({ video: videoName, bytes: fs.statSync(video).size, sha256: digest(video), source_files: snapshot.length, chapters: timeline.chapters.length, captions: cues.length, craft_warnings: check.craft.warningCount }, null, 2));
