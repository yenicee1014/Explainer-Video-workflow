// Run a repository HTTP server before this optional browser verification.
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const destination = path.join(root, "projects/nasa-punk/verification");
const url = process.env.PREVIEW_URL || "http://127.0.0.1:3034/nasa-punk.html";
const executablePath = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const timeline = JSON.parse(await fs.readFile(path.join(root, "projects/nasa-punk/source/rebuild-timeline.json"), "utf8"));
const browser = await puppeteer.launch({ executablePath, headless: true });
const report = {
  status: "running", viewports: [], chapters: [], frame_samples: [],
  scope: "Browser metadata, playback, pause, chapter seeks, subtitle loading, nonblank decoded samples, responsive bounds and missing-media handling. Not a full human audio/visual review.",
};
try {
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  const pageErrors = [];
  const networkErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("response", (response) => {
    if (response.status() >= 400) networkErrors.push({ path: new URL(response.url()).pathname, status: response.status() });
  });
  await fs.mkdir(destination, { recursive: true });
  for (const viewport of [{ width: 1440, height: 1080 }, { width: 390, height: 844 }]) {
    await page.setViewport(viewport);
    const response = await page.goto(url, { waitUntil: "networkidle0" });
    assert.equal(response.status(), 200);
    await page.waitForFunction(() => document.querySelector("video").readyState >= 1);
    const layout = await page.evaluate(() => {
      const video = document.querySelector("video");
      return {
        overflow: document.documentElement.scrollWidth > innerWidth,
        duration: video.duration, video_width: video.videoWidth, video_height: video.videoHeight,
        chapterCount: document.querySelectorAll("[data-time]").length,
        outOfBounds: [...document.querySelectorAll("h1, p, nav a, li a")].filter((el) => {
          const bounds = el.getBoundingClientRect();
          return bounds.left < 0 || bounds.right > innerWidth + 1;
        }).map((el) => el.textContent.trim()),
      };
    });
    assert.equal(layout.overflow, false);
    assert.deepEqual(layout.outOfBounds, []);
    assert.equal(layout.chapterCount, 14);
    assert.equal(layout.video_width, 1280);
    assert.equal(layout.video_height, 720);
    assert.ok(Math.abs(layout.duration - timeline.duration) < 0.1);
    await page.evaluate(async () => {
      const video = document.querySelector("video");
      video.muted = true;
      await video.play();
    });
    await page.waitForFunction(() => document.querySelector("video").currentTime > 0.2);
    await page.evaluate(() => document.querySelector("video").pause());
    const pausedAt = await page.evaluate(() => document.querySelector("video").currentTime);
    await new Promise((resolve) => setTimeout(resolve, 200));
    assert.equal(await page.evaluate(() => document.querySelector("video").currentTime), pausedAt);
    await page.evaluate(() => { document.querySelector("video").currentTime = 335; });
    await page.waitForFunction(() => {
      const video = document.querySelector("video");
      return !video.seeking && video.readyState >= 2 && Math.abs(video.currentTime - 335) < 0.1;
    });
    await page.evaluate(() => window.scrollTo(0, 0));
    const screenshot = `player-${viewport.width}.jpg`;
    await page.screenshot({ path: path.join(destination, screenshot), fullPage: true, type: "jpeg", quality: 85 });
    report.viewports.push({ ...viewport, ...layout, playback: true, pause_stable: true, screenshot });
  }
  for (const chapter of timeline.chapters) {
    await page.click(`[data-time="${Number(chapter.start.toFixed(6))}"]`);
    await page.waitForFunction((target) => {
      const video = document.querySelector("video");
      return !video.seeking && video.readyState >= 2 && Math.abs(video.currentTime - target) < 0.6;
    }, {}, chapter.start);
    const time = await page.evaluate(() => {
      const video = document.querySelector("video");
      video.pause();
      return video.currentTime;
    });
    assert.ok(Math.abs(time - chapter.start) < 0.6);
    report.chapters.push({ id: chapter.id, target_seconds: chapter.start, actual_seconds: time, ok: true });
  }
  await page.evaluate(() => { document.querySelector("track").track.mode = "hidden"; });
  await page.waitForFunction(() => document.querySelector("track").track.cues?.length === 67);
  report.subtitle_cues = 67;
  for (const time of [20, 207, 335]) {
    await page.evaluate((time) => { document.querySelector("video").currentTime = time; }, time);
    await page.waitForFunction((time) => {
      const video = document.querySelector("video");
      return !video.seeking && video.readyState >= 2 && Math.abs(video.currentTime - time) < 0.1;
    }, {}, time);
    const sample = await page.evaluate(() => {
      const canvas = document.createElement("canvas");
      canvas.width = 128;
      canvas.height = 72;
      const context = canvas.getContext("2d");
      context.drawImage(document.querySelector("video"), 0, 0, canvas.width, canvas.height);
      const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
      const levels = [];
      for (let index = 0; index < pixels.length; index += 4) levels.push(pixels[index] + pixels[index + 1] + pixels[index + 2]);
      return { min: Math.min(...levels), max: Math.max(...levels), distinct: new Set(levels).size };
    });
    assert.ok(sample.max - sample.min > 100 && sample.distinct > 50, `Blank decoded frame at ${time}`);
    report.frame_samples.push({ time_seconds: time, ...sample });
  }
  assert.deepEqual(pageErrors, []);
  assert.deepEqual(networkErrors, []);
  report.page_errors = pageErrors;
  report.network_errors = networkErrors;
  const missing = await browser.newPage();
  await missing.setRequestInterception(true);
  missing.on("request", (request) => {
    if (request.url().includes("nasa-punk-full-rebuild.mp4")) request.abort();
    else request.continue();
  });
  await missing.goto(url, { waitUntil: "networkidle0" });
  await missing.click("[data-time='12']");
  await missing.waitForFunction(() => /视频加载失败|暂时不能加载视频/.test(document.querySelector("#playback-status").textContent),
    { timeout: 20000 });
  report.missing_media_message = await missing.$eval("#playback-status", (el) => el.textContent);
  report.status = "passed";
  await fs.writeFile(path.join(destination, "browser-check.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
