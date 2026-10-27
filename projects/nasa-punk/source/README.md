# 源码快照与复用说明

这是本次成片的核心源码快照，**不是自包含、开箱即用的重渲染包**。运行前需要自行补齐合法素材、字体、GSAP、配音与工具依赖。缺少必需资源时应停止构建，不静默回退为空白或示意图。

## 文件导航

| 文件 | 用途 |
| --- | --- |
| `rebuild-script.json` | 14 章、67 句重新编写的旁白文本 |
| `rebuild-timeline.json` | 实测录音的全局 / 局部秒数、时长和句级锚点 |
| `scripts/prepare-rebuild-audio.mjs` | Tingting 逐句合成、FFmpeg 静音检测与时间轴生成 |
| `scripts/prepare-rebuild-assets.py` | 参考帧裁切、四点校正、手册页提取与来源记录 |
| `scripts/rebuild-scenes.mjs` | 场景 SVG、GSAP 动作与语义动作说明 |
| `scripts/build-full.mjs` | 生成独立场景、主片、字幕、动作说明与字体子集 |
| `scripts/mix-rebuild.py` | 合成程序配乐、摆放旁白并混音 |
| `scripts/hyperframes.mjs` | 在 npm 缓存中查找固定版 HyperFrames 的原 wrapper |
| `index.html` / `compositions/*.html` | 本次已生成的主片与 14 场 HTML，不是静态网站播放器 |
| `index.motion.json` | 字标样段的可自动检查动作断言，非全片语义验收 |
| `compositions/*.beats.json` / `STORYBOARD.md` | 录音锚点、对象变化、讲解动作与停留 |
| `assets/rebuild/provenance.json` / `assets/sources.json` | 静帧、手册、字体与字标的来源元数据 |
| `assets/licenses/` | 本地可用的字体许可文本，不包含字体文件 |

## 当前明确缺少的文件

- `reference/source.mp4` 与 `reference/frames/`：参考作品和抽帧，不公开。
- `assets/rebuild/*` 图片及手册扫描、`assets/images/nasa.svg`：只保留元数据，不提供第三方素材包。
- `assets/fonts/Archivo.ttf`、`SpaceMono-Regular.ttf`、`NotoSansSC-Regular.otf`、`NotoSansSC-Bold.otf` 及生成的 WOFF。
- `assets/vendor/gsap.min.js`。
- `assets/rebuild-voice/*` 逐句录音、`assets/rebuild-mix.wav`、`assets/rebuild-mix.m4a`。
- Node / Python 运行环境、FFmpeg、HyperFrames、渲染缓存与 npm 缓存。

上面的 HTML 会引用这些缺失资源；不要把不能完整打开的源码预览误认为本次已发布的 MP4 有同样问题。播放已导出视频无需安装上述工具。

## 原本地构建环境与命令

本次实际使用 HyperFrames `0.8.201`；不是“最新版本”承诺。环境为 macOS、Node.js 22+、Python 3、FFmpeg，以及 numpy、Pillow、PyMuPDF、OpenCV、fontTools。系统 `say` 需要 Tingting。此目录没有独立依赖锁文件，不保证不同环境或不同声音版本逐帧、逐样本一致。

原 wrapper 从 npm 缓存寻找固定版本，不会自动下载安装。先自行准备对应工具与合法资源；**仅在资源齐全后**原执行顺序是：

```sh
node scripts/prepare-rebuild-audio.mjs
python3 scripts/mix-rebuild.py
npm run build
npm run check
npm run dev
npm run render
```

素材准备脚本依赖参考抽帧和本地 PDF，并不是一个会自动下载全套素材的安装器。只需要复用方法时，重点阅读场景生成器、统一时间轴和混音脚本；替换为自己的内容与合法素材后另建项目。

重新合成旁白会改变时长，应重建全部时间轴、字幕与动画，不沿用原章起点。当前源码用于理解本次生产方式，不把依赖缺失状态描述为复现成功。
