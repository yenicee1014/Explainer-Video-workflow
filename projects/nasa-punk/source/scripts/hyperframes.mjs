import {existsSync, readdirSync, readFileSync} from "node:fs";
import {homedir} from "node:os";
import path from "node:path";
import {spawnSync} from "node:child_process";

const candidates = [];
const cache = path.join(homedir(), ".npm", "_npx");
const project = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8"));
const pinnedVersion = project.production.hyperframes;
if (existsSync(cache)) {
  for (const item of readdirSync(cache)) {
    const base = path.join(cache, item, "node_modules", "hyperframes");
    const manifest = path.join(base, "package.json");
    if (!existsSync(manifest)) continue;
    const metadata = JSON.parse(readFileSync(manifest, "utf8"));
    if (metadata.version === pinnedVersion) {
      candidates.push(path.join(base, "bin", "hyperframes.mjs"));
    }
  }
}
if (!candidates.length) {
  throw new Error(`HyperFrames ${pinnedVersion} missing. Install the pinned version before rendering.`);
}
const result = spawnSync(process.execPath, [candidates[0], ...process.argv.slice(2)], {
  stdio: "inherit",
  env: process.env,
});
if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
