# ComfyUI 工作流与复用

本页描述 V2 实际制作链和公开版本的环境适配。`history/demo/COMFY_WORKFLOW.md` 是更早的方案记录，其中“待开发”等字样属于当时状态。当前节点与入口以本页为准。

## 三种使用方式

| 目标 | 需要什么 | 会否调用生成服务 |
| --- | --- | --- |
| 播放最终视频 | 网页或 MP4 | 不会 |
| 修改现有字排并重渲染 | Python、FFmpeg、中文字体、Release 素材包 | 不会 |
| 重新生成或更换主题 | 上述环境、ComfyUI、AutoDL 插件与自己的账户、修改后的分镜 | 会，可能计费 |

## 1. 安装本地依赖

Python 建议 3.10 以上，命令中的 `python3` 应指向选定环境。FFmpeg 与 ffprobe 必须在 PATH 中，或通过 `SC_FFMPEG`、`SC_FFPROBE` 指定。

```sh
cd projects/skyscraper-crisis
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python reproduce.py check
```

同一组依赖也应安装到 ComfyUI 实际使用的 Python 环境中。中文字体使用本机安装版本；Linux 可使用 Noto CJK，具体字体路径见 `.env.example`。本片当时使用 macOS 黑体、宋体与 Arial，跨系统替换字体后需重新检查换行、宽度和版式。

环境变量由 shell 或 ComfyUI 启动配置加载，项目不会自动读取 `.env`。需要手动配置时：

```sh
cp .env.example .env
# 编辑 .env 中的实际路径，再在当前 shell 加载
source .env
```

## 2. 下载重渲染素材包

```sh
.venv/bin/python reproduce.py fetch-assets
.venv/bin/python reproduce.py check
```

此命令下载同次 Release 的 `skyscraper-crisis-v2-render-assets.zip`，先核对整个压缩包 SHA-256，再逐文件核对和安全解压。已存在且哈希正确的文件直接复用；如本地有不同内容会停止，避免覆盖自己的修改。

素材包包含 23 条采用的 V2 机制镜头、8 条 V1 中继续使用的补充镜头、8 章最终旁白混音、5 张最终采用的具名建筑/历史照片。

每段旁白的文字与词级时序位于仓库中的 `full-film/01–08/voice.json`。逐句 MP3/WAV 缓存不影响现有混音重渲染，因此未全部打包。网页缓存和被弃用地标候选视频也不作为重渲染输入。

第三方摄影的来源和许可状态见 `full-film-v2/research/photos.json`。素材包不是一套重新授权的商用素材库。

## 3. 无云任务的本地重渲染

```sh
.venv/bin/python reproduce.py plan
.venv/bin/python reproduce.py render --chapter 3
```

不传 `--chapter` 会按 01–08 顺序重渲染全部章节。所有章节完成后：

```sh
.venv/bin/python reproduce.py assemble
```

渲染读取 `full-film/NN/narration.wav` 与 `voice.json`，由 `v2_visuals.py` 按句段、关键词切镜和 `BEATS` 合成。`reproduce.py` 在内存中将相对音频路径解析到项目目录，不需要恢复作者电脑路径。

输出是项目内 `full-film-v2/NN/chapter-NN.mp4` 和完整中文版 MP4。它不会修改仓库 `video/` 中已经发布的原始交付文件。跨字体、FFmpeg 或依赖版本的再次渲染不保证和交付视频字节相同。

## 4. 在 ComfyUI 安装本项目节点

将 `comfyui/custom_nodes/skyscraper_editorial/` 整个目录复制或链接到自己 ComfyUI 的 `custom_nodes/`。启动 ComfyUI 前设置：

```sh
export SC_PROJECT_DIR="/absolute/path/to/Explainer-Video-workflow/projects/skyscraper-crisis"
export SC_COMFY_DIR="/absolute/path/to/ComfyUI"
export SC_COMFY_URL="http://127.0.0.1:8190"
```

默认从源码所在仓库查找项目；复制到其他位置时应显式设置 `SC_PROJECT_DIR`。重启 ComfyUI 后检查节点：

```sh
curl -fsS http://127.0.0.1:8190/object_info/SCSceneBatch
curl -fsS http://127.0.0.1:8190/object_info/SCFullChapter
```

| 节点 | 输入 | 行为 |
| --- | --- | --- |
| `SCSceneBatch` | chapter 1–8、workers 1–3、revision、可选 previous VIDEO | 对本章的缺失情境素材调用已安装的 `AutoDLWorkflow`；已缓存素材复用 |
| `SCFullChapter` | chapter 1–8、revision ≥20 | 使用已备齐的媒体、旁白和时序在本地合成对应章节 |
| `LoadVideo` → `SaveVideo` | 已完成 MP4 | 本地预览与导出，不负责素材生成 |

公开节点只注册 V2 所需的两个项目节点；早期 demo 所用的 `SCNarration`、`SCEditorialRender` 等见历史记录，不属于本次安装入口。

`SCFullChapter` 的合成由项目 Python/Pillow/FFmpeg 执行，并由 ComfyUI 节点触发；它不是全部依靠 ComfyUI 原生图像节点实现的时间轴。

## 5. 生成入口与 API 入口

将 `full-film-v2/workflow-generation.json` 拖入 ComfyUI：8 个 `SCSceneBatch` 通过 `previous` 链接，保证 01→08 顺序。每章最多同时生成 3 条，本片历史执行参数为 3；服务端并发限制应按自己的账户调整。

将 `full-film-v2/workflow-preview.json` 拖入 ComfyUI：先把仓库 `video/skyscraper-crisis-v2-full.mp4` 复制到 ComfyUI input，命名为 `skyscraper-v2-full-film.mp4`，即可通过 `LoadVideo` 播放成片。

API JSON 以 `class_type` 为字段，不是画布 JSON。典型素材图：

```text
AutoDLWorkflow
  workflow_id = minimax_h3_lightx2v_no_pic
  ad_text_01  = 完整镜头提示词
  ad_text_02  = 768p横
  ad_int_01   = 8 秒
  ad_int_02   = seed
       ↓ VIDEO
AutoDLPreviewVideo
```

每条真实调用图在 `full-film-v2/assets/<id>/workflow-api.json`。可以在本机 ComfyUI 使用适配的 API 提交：

```sh
curl -fsS "$SC_COMFY_URL/prompt" \
  -H "Content-Type: application/json" \
  --data-binary @request.json
```

`request.json` 必须是 `{"prompt": <工作流API对象>, "client_id": "<自己的标识>"}`，不能直接把画布 JSON POST 给 `/prompt`。

按章节的生成/渲染 API 保存在 `full-film-v2/01–08/workflow-*-api.json`。安装节点后，也可使用：

```sh
.venv/bin/python v2_pipeline.py generate
.venv/bin/python v2_pipeline.py render --revision 21
.venv/bin/python v2_pipeline.py assemble
```

`revision 20` 是本次交付的画面版号；修改合成代码后提高 revision 才会绕开已有章核验缓存。生成缓存另由素材 ID 与文件决定，不能只提高 revision 就以为旧素材必然重生。

## 6. 云服务与缓存恢复

本片使用的是已安装 `ComfyUI-AutoDL-API` 的 `AutoDLWorkflow`、`AutoDLPreviewVideo`。本仓库不重新分发第三方插件，不带账户设置。插件来源和当前目录应自行核实；不要将私人 token 写进 JSON。作者当时使用的插件仓库上游地址记录在 `environment.json`。

本次的远端 schema 是历史快照，未来可能改变。生成前先确认自己的节点已注册、目录存在、字段映射相符、账户可用。查阅价格与限制应以当时服务端信息为准。

生成参数：8 秒、`768p横`、明确 seed、超时 1800 秒、每 5 秒查询。本片没有独立负面提示词字段；也不能把文生视频图写成支持参考视频或图像的图。

重复运行会复用 `motion.mp4` 与 `result.json`。若发现 `batch-v3-submission.json` 或先前提交标记，但结果缺失，脚本会停止自动重提，避免因为下载失败重复生成。此时应先核对既有 ComfyUI history 与云任务，恢复原结果。

公共源码没有复制作者的提交标记、临时结果 URL 或历史账户任务。下载素材包后，本地复用脚本会为已核验的素材补最小缓存记录；这不代表在你的账户重新生成过。

## 7. 从头生成旁白与补充素材

无需复现相同旁白时，可先修改台词，再运行：

```sh
.venv/bin/python full_film.py plan
.venv/bin/python full_film.py voices
```

声音是 `zh-CN-YunxiNeural`，rate `+0%`、pitch `-3Hz`，词级边界保存用于字幕和关键词切镜。`edge-tts` 需要网络；更换服务或声音后，实际时长与字幕边界必须重算。

V2 仍引用 V1 的 8 条补充镜头；素材包已包含它们。从零开始且没有素材包时，对 1–8 逐一运行 `full_film.py generate --chapter N`，再执行 V2。最终照片可依据 `photos.json` 中的 URL 重新取得；`v2_prepare_references.py` 是当时页面结构的抓取方法，网站结构变化后需要重新核对。

## 8. 验收

按 `PROMPTS.md` 中每条 brief 和三帧核对图审查人物动作，再检查 78 段执行表。具名建筑检查完整轮廓；不可读的生成纸面文字不作为证据。

`v2_pipeline.py assemble` 会检查原旁白不变、素材存在、章节音画时长，并完整解码。其 `make_plan()` 会生成当前计划，建议开始修改前先保存自己的版本。最后检查输出、六类核对片和 `delivery-manifest.json`，将后续变化追加到 `ITERATIONS.md`。
