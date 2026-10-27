# 核验范围与状态

这里分开记录本地制作阶段已有的检查与本次发布检查。报告中的路径已改成项目相对路径，不含本机绝对路径；数值、警告和范围保留。

## 制作阶段记录

- [HyperFrames 原检查报告（仅路径脱敏）](final-check.json)
- [成片 ffprobe 媒体参数](full-media-probe.json)
- [原混音与成片音轨数值同步检查](audio-sync-check.json)
- [导出状态记录（补充原报告中的 craft 警告范围）](production-status.json)

| 检查 | 记录结果 | 局限 |
| --- | --- | --- |
| lint | 扫描 15 个 HTML，0 错误 / 0 警告 | 不负责事实与语义 |
| runtime | 0 错误 / 0 警告 | 不证明全片每帧正确 |
| layout | 0 错误 / 0 警告，1 条信息级裁切记录 | 报告采样点为 198、201、249 秒；不是穷尽全片 |
| motion | 断言通过，采样数 300 | 断言主要针对字标顺序与边界，不覆盖全部讲解动作 |
| contrast | 抽样 9 项通过 | 报告采样点为 198、201、249 秒；不等于所有文字可读性验收 |
| craft | **38 条警告** | 30 条 `dead_stretch`、6 条 `text_below_floor`、2 条 `line_unread`；有停顿可能是阅读需要，仍待人工判断 |
| 媒体输出 | 358.466667 秒，H.264 / AAC，10,754 帧 | 文件可解码不等于内容正确 |
| 数值音频同步 | 1、180、330 秒，各 15 秒，偏移约 10.7ms，相关系数均 >0.992 | 只比对源混音与输出波形，不是旁白 / 字幕 / 画面语义核对 |

制作记录还包括：先行 31 秒样段、字标连续帧、全片关键帧、首中尾抽帧及完整文件解码无错。相关结论是制作记录，不冒充人类完整听看报告。

## 本次公开文件检查

[delivery-manifest.json](../delivery-manifest.json) 保存公开 MP4 的大小、SHA-256、实际媒体参数及章节秒数；[publication-check.json](publication-check.json) 由发布检查脚本生成，检查字幕与句级时间轴一致、章节链接、文件路径、源码语法及排除文件，并重新探测及完整解码 MP4。

复核命令（仓库根目录）：

```sh
python3 tools/check_nasa_punk.py --media
python3 -m unittest discover -s tests -v
git diff --check
```

CI 使用 `python tools/check_nasa_punk.py --check-only` 复核文件完整性与发布结构，不安装 FFmpeg，也不覆盖本地完整媒体检查报告。

### 播放器检查

[browser-check.json](browser-check.json) 记录 1440×1080 和 390×844 浏览器视口的检查：播放、暂停、14 章跳转、67 条 WebVTT 字幕、三个时间点的非空解码帧、页面横向边界，以及视频请求失败后的提示。截图见 [桌面](player-1440.jpg) 与 [手机](player-390.jpg)。这验证浏览器交互与抽样解码，不是全片人工听看。

安装根目录的锁定开发依赖、准备 Chrome，并使用支持 HTTP Range 的静态服务器（例如 `serve`）托管仓库后运行：

```sh
npm ci
PREVIEW_URL=http://127.0.0.1:3035/nasa-punk.html node tools/check_nasa_punk_browser.mjs
```

Chrome 路径可通过 `CHROME_PATH` 设置。Python 自带的简单 HTTP 服务器不支持本次测试所需的分段读取，不用于章节跳转测试。

仓库原有的天气项目构建与测试只验证其各自范围，不拿旧项目通过结果代替 NASA 朋克检查。

## 仍未完成

- 全片正常速度人工听看与逐字人工校对。
- 词级对齐及所有句内动作的关键词校准。
- 对 38 条 craft 提示逐条人工判断与处理。
- 逐项外部图像及系统语音再分发许可确认。

因此公开状态为：**全片已导出并完成媒体 / 自动核验，人工语义验收和部分权利确认待完成**，不是零警告、不是逐帧复刻完成。
