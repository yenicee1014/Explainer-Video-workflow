# 繁荣的高度：10 秒试片

成片：`renders/skyscraper-demo-v1.mp4`，1280×720、25 fps、H.264/AAC、10 秒。

参考片只用于提取灰白纸纹、黑白建筑剪贴、暗红强调和科普字幕等视觉特征。旁白、标题、版式与动画为本项目重新创作。建筑是 AI 生成的示意素材，不作为真实历史建筑或统计证据。

## ComfyUI 工作台

本机地址：`http://127.0.0.1:8190`。

打开「繁荣的高度 - 成片与本地重剪」，或导入 `workflow-cached.json`。此工作流从本机读取已生成的素材，运行不会再提交云端任务。原有 8188 实例保持运行。

重启工作台：

```sh
./ComfyUI/ComfyUI/.venv/bin/python3 videos/skyscraper-crisis-original/run_demo.py start
```

命令的工作目录为 `$WORKSPACE`。节点定义位于 `ComfyUI/ComfyUI/custom_nodes/skyscraper_editorial`，画面和声音的实现位于本目录 `editorial.py`。

## 实际生成记录

- Grok 单图请求返回 HTTP 403，没有图片返回；未重试该请求。
- 使用已安装的 AutoDL ComfyUI 节点，提交一次 H3 文生视频任务。
- 远端任务：`57edcd89-7aa3-45ea-8394-8660166af56f`。
- 工作流：`minimax_h3_lightx2v_no_pic`，5 秒、768p 横屏。
- 原始素材：`assets/h3-building-motion.mp4`，1344×768、24 fps。
- 完整生成提示词保存在 `workflow-h3-api.json`。
- 本机去除素材黑色留边、抠出建筑、放慢动态、重新编排三个画面，添加中文旁白、字幕、原创低频底音与纸张短音。
- 旁白：Microsoft Edge `zh-CN-YunxiNeural`。
- 可视抽查：`renders/contact-sheet.jpg`。
- 媒体参数和配音信息：`renders/verification.json`。

仅完成本页所述试片；未制作参考视频全长。云端实际扣费以服务商账单为准。
