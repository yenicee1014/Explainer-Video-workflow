# 第三方来源与公开分发边界

## 科学资料

18 条资料以 `projects/weather-ai/sources.json` 为准，记录标题、原始 URL、使用范围和局限。仅引用并由原创讲稿解释，不包含原站图片、论文全文或下载数据。来源条目不意味着授权转载来源作品。

## 设计参考

https://github.com/LBEILC/RhineLabUI 仅作为信息分层和档案式界面的参考。本仓库实际视觉为黑／米白／红瑞士排版，图形由本仓库 Python 代码生成。没有复制其源代码、品牌、模型、PV 或其他素材；无合作或背书关系。

## 字体

本地原稿使用 MiSans。官方许可页面 https://hyperos.mi.com/font/en/download 于 2026-10-19 核对，含免费使用条件，也含禁止单独再分发字体及再分发字体软件副本等限制。为避免把使用权等同于字体文件再分发权，公开版本**不包含 MiSans 字体二进制文件**，改用系统字体。`projects/weather-ai/assets/licenses/MiSans-license.pdf` 仅保留原稿随附许可说明，不能理解为本仓库提供 MiSans 字体再授权。

公开版系统字体栈为 `system-ui, PingFang SC, Microsoft YaHei, sans-serif`。字体由观看设备提供，跨系统外观可能不同。原始本地字体和项目未改动。

## 声音

原本地审阅稿使用 macOS `say` 的 Eddy 中文合成声音。当前未核实生成音频的公开再分发条件，因此不公开声音文件、语音缓存或调用本机系统声音的生成节点。公开版本 `timeline.json` 明确标记 `audio: false`。

## 可选工具依赖

`puppeteer-core` 仅用于开发检查，精确版本见 `package-lock.json`；使用其上游许可证（Apache-2.0）。Node.js、Chrome/Chromium、ComfyUI、Python 均不捆绑在仓库中，各自适用上游许可。使用 ComfyUI 不代表本项目授予其许可之外的权利。

## 本仓库原创部分

尚未选定通用开源许可证；原创代码、讲稿与图解保留版权。公开可见和可下载不等于已授予任意商用、再分发、改编或再许可的权利。如需此类使用，请先联系仓库维护者确认。第三方内容不因与本项目同时出现而改变其许可。
