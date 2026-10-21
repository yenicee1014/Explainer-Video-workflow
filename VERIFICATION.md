# 公开版本验证记录

本记录对应仓库中的无声字幕动画版本，以及新版天气照片版第一章无声 MP4；不沿用本地带配音稿的测试结果。

## 已执行

- Python 3.9.6：标准库构建成功；40 场景、8 章节、167 句字幕，947.0416875 秒，画布 1080×1920。
- `python3 tools/check_content.py`：40 幅 SVG XML、来源 ID、字幕与讲稿一致性、雨区几何和示例算术检查通过。
- `python3 -m unittest discover -s tests -v`：14 项回归通过，包括过期元数据、错误字幕、时间不连续、未知来源、非有限时间及越界工程路径的拒绝测试。
- ComfyUI 0.34.0 / Python 3.13.12 / CPU：真实执行公开 API 图，5 节点、4 连接成功。仅加载公开节点，未加载付费 API 插件。详见 `reports/comfy-check.json`。
- Chrome 自动化（历史无声 SVG 工程）：40 场 SVG 文本边界、相同时间乱序定位的像素一致性、8 章节跳转、播放/暂停/结尾检查通过。报告与播放器截图见 `reports/`。
- 新版第一章从本地浏览器预览导出无声 MP4：H.264、1080×1920、114.6852 秒，仅一个视频流，无音频流；文件位于 `video/weather-real-preview-chapter1-silent.mp4`。本地另有一份 114.6821 秒的 AV1 导出，经校验与公开版内容一致，未重复上传。

## 环境与限制

- Python 代码在 3.9.6 本地执行过；文档推荐 Python 3.10+。仓库包含 3.10/3.13 的持续集成配置，远程执行结果以 GitHub Actions 为准。
- ComfyUI 启动日志出现其本地数据库初始化警告；HTTP 服务和本次 API 执行成功。本次验证不涵盖该数据库功能或其他 ComfyUI 插件。
- 系统字体的跨设备差异、所有文本的相互遮挡、完整 15 分 47 秒人工逐字审阅，均不在以上自动化检查的保证范围；新版第一章 MP4 已完成文件级核验，但未完成完整人工逐帧审阅。
- `sources.json` 中的 `verified` 是原内容研究阶段的标记，构建检查只核对引用关系，未重新访问每条来源。
- 本项目尚无外部气象专家审签；新版第一章已完成无声 MP4 导出和文件级核验，但全片成片与人工完整审阅仍未完成。当前公开交付包括浏览器动画源工程、第一章无声 MP4 和无声 ComfyUI 工作流。

## 重跑

先运行 `python3 tools/build.py`、`python3 tools/check_content.py` 和 Python 回归测试。

浏览器验证是可选开发步骤：执行 `npm ci --ignore-scripts`，启动仓库根目录的本地 HTTP 服务后运行 `npm run test:browser`。默认地址为 `http://127.0.0.1:3033/projects/weather-ai/`；`PREVIEW_URL` 可覆盖地址，`CHROME_PATH` 可指定本机 Chrome/Chromium 程序。依赖固定在 `package-lock.json`，浏览器不由安装脚本下载。

真实 ComfyUI 验证需要先安装本仓库节点并启动本机 ComfyUI，再运行 `python3 tools/check_comfy.py --url http://127.0.0.1:8190`。这个步骤会生成图解、字幕和报告，不导出视频、不调用语音服务。
