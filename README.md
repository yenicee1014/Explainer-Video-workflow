# 天气预报 × AI：为什么还会报不准？

天气科普项目的公开工作流与版本档案。当前创作方向保留奶油白、黑色、红色强调的已确认排版，并以真实、可追溯的天气照片补足具象画面；抽象概念仍使用明确标注的原创教学图解。

> **当前版本：第一章真实照片版本地预览，并已导出无声 MP4。** 画面长约 1 分 54 秒，1080×1920，五个场景、22 条句级字幕；全稿其余章节尚未完成视觉制作。全稿约 16 分 39 秒的本地配音并不等于完整成片。公开 MP4 只含画面，不含许可尚未核实的系统女声。

## 可点击播放

- [点击在线播放第一章无声视频（1 分 54 秒）](https://yenicee1014.github.io/Explainer-Video-workflow/)
- [直接打开 MP4](https://yenicee1014.github.io/Explainer-Video-workflow/video/weather-real-preview-chapter1-silent.mp4)
- [仓库中的 MP4 文件](video/weather-real-preview-chapter1-silent.mp4)（GitHub 文件页可能仅显示下载入口，请优先使用上方在线播放链接）

该仓库现在公开第一章 1 分 54.68 秒的竖屏画面导出，已确认视频编码为 H.264，便于浏览器直接播放；文件仅含视频流、无音轨。浏览器本地预览仍保留普通话声音；完整全片和有声 MP4 尚未完成。

## 当前版本说明

- [第一章创作方向、照片出处与配音纠错说明](docs/REAL-PHOTO-MANDARIN.md)
- [实际制作与本地核验流程](docs/REAL-PHOTO-WORKFLOW.md)
- [ComfyUI 照片 Lanczos 重采样 API 示例](workflows/weather-photo-resample-api.json)
- [科学与素材授权边界](docs/SCIENCE-AND-RIGHTS.md)
- [当前交付状态](docs/PROJECT-STATUS.md)

### 创作原则

1. 真实云照片只呈现云的形态，不作为某次天气预报准确性的证据。
2. 1973 年 NOAA/NSSL 雷达设备历史照片只说明设备外观，不冒充现代雷达回波。
3. 城市范围、发布时间、有效时间和雨区偏差用原创示意图表达；不把示意图伪装成实测数据。
4. 照片只作来源清楚的裁切、缩放与克制推近。ComfyUI 重采样不使用扩散模型，也不生成新的天气图案。
5. 普通话女声使用本机 macOS 离线声音。系统声音再分发许可尚未核实，旁白与逐句缓存留在本地，不上传。

## 预览与可复现范围

第一章在本地使用浏览器预览。字幕按句级音频时间同步，并已完成本地播放、定位、场景同步及手机布局检查。语音更换原因、校验方法和检查的局限见当前版本文档。

本仓库的现有可执行 SVG 源工程 `projects/weather-ai/`、ComfyUI 工作流、构建工具与测试是早期无声版本材料。其约 15 分 47 秒的长度、40 幅 SVG 和历史检查报告不代表新版第一章的真实照片画面或配音核验结论；旧结果不得套用于新版。

## 早期源工程构建（历史版本）

仓库仍保留早期无声 SVG 工程，供版本追溯与代码参考。在仓库根目录可运行：

```sh
python3 tools/build.py
python3 tools/check_content.py
python3 -m unittest discover -s tests -v
python3 -m http.server 3033 --bind 127.0.0.1
```

打开 <http://127.0.0.1:3033/projects/weather-ai/>。这会运行**历史无声 SVG 工程**，不是新版第一章照片预览。历史检查结果在 `VERIFICATION.md`；其范围只对该历史版本有效。

## 公开内容与许可

本仓库分享工作流、创作记录与来源，不包含本机离线配音、逐句 WAV/AIFF、系统声音缓存、模型权重、凭证或私人路径。已核验的公开照片来源与许可说明分别链接于 Wikimedia Commons：

- [积雨云照片](https://commons.wikimedia.org/wiki/File:Cumulonimbus_incus_cloud_Jan2008.jpg)
- [NOAA/NSSL 历史雷达设备照片](https://commons.wikimedia.org/wiki/File:Doppler_Weather_Radar_-_NOAA.jpg)

源代码、讲稿、图解与第三方素材的版权范围不同；仓库尚未选定通用开源许可证。公开可见不代表任意商用、改编或再分发许可。详情见 [第三方说明](THIRD_PARTY_NOTICES.md)。

---

## 持续迭代：新增《繁荣的高度》（2026-10-25）

本仓库持续积累不同主题的科普视频工作流。**以上天气项目 README 原文保留**，其版本状态、无声导出和配音说明继续只描述天气项目；以下是新加入的经济科普项目，不覆盖天气工程，也不把历史试验描述为最终结果。

本次主题是：**摩天大楼、商业地产与经济周期之间究竟有什么关系？**《繁荣的高度》从历史时间线出发，用一个虚构办公楼项目解释借贷、竞争、建设滞后、租户减少、再融资与证据检验。叙事重点是项目怎样承压，以及为何不能把建筑纪录直接当作危机预报。

- [在线播放完整版：有配音和字幕](https://yenicee1014.github.io/Explainer-Video-workflow/skyscraper.html)
- [仓库内完整版 MP4](video/skyscraper-crisis-v2-full.mp4)
- [直接播放 / 下载 MP4](https://yenicee1014.github.io/Explainer-Video-workflow/video/skyscraper-crisis-v2-full.mp4)
- [六类经济现象核对片](video/skyscraper-crisis-v2-highlights.mp4)
- [完整项目说明与复用步骤](projects/skyscraper-crisis/README.md)

此次上传的是用户所指的“11 分 06 秒”V2 原文件，未剪短、未静音。`ffprobe` 精确时长为 **666.581333 秒（11:06.58，四舍五入约 11:07）**，1280×720、25fps、H.264 视频与 AAC 音频。文件大小、SHA-256 和媒体参数见 [交付清单](projects/skyscraper-crisis/delivery-manifest.json)。

### 八章主题与细分内容

| 章节 | 内容 | 必须出现的具体情节 |
| --- | --- | --- |
| 01 同一座城市，两种消息 | 建筑纪录与经济下行并置 | 帝国大厦开幕、工厂锁门、工人离岗、银行排队、迪拜事件时间线 |
| 02 先把时间摆对 | 区分股灾、宣布、开工、封顶、营业 | 交易所、钢结构施工、事先确定检验窗口 |
| 03 一栋楼，先在账本里建起来 | 成本、贷款、预期租金与合同义务 | 项目图纸、预算、银行递笔签约、企业看房与新增工位 |
| 04 每个人的算盘，都指向了同一个未来 | 多项目供应叠加与共同乐观预期 | 四个独立工地、多楼盘争取有限租户、开发商与银行及投资者讨论 |
| 05 楼盖的是过去，市场活在现在 | 建设周期与需求变化 | 双子塔时间线、取消扩张、撤电脑与堆椅子、未完工核心筒 |
| 06 楼没有倒，账却可能撑不住 | 租金下滑、到期续贷、估值与信贷传导 | 搬箱交钥匙、空工位、旧合同与新方案、估值检查、退回贷款申请 |
| 07 为什么这个“指数”总让人印象深刻 | 选择偏差、完整样本与预测检验 | 扩展案例集合、正反案例、论文书目、先定标准再开新资料 |
| 08 真正值得看的，是哪几个问题 | 需求、资金、到期与承受能力 | 压力预算、租约与账本核对、下一笔到期日 |

### 从 Demo 到 V2 的迭代

| 阶段 | 当时结果或问题 | 后续调整 |
| --- | --- | --- |
| 视觉 Demo | 灰白纸纹、黑白剪贴与暗红强调得到方向认可；素材集中在一栋楼 | 先写完整科普台词 |
| 完整台词 / V1 | 8 章、78 段旁白完成；泛化工人与高楼画面无法解释具体台词 | 建立逐段“台词 → 主体 → 动作 → 证据”映射 |
| V2 情节重制 | 新增 23 条采用的经济机制素材，形成 148 个摄影画面节拍 | 加入签约、竞争、搬离、续贷、样本检验，并保留原旁白 |
| 建筑准确性纠偏 | 两条生成地标候选轮廓偏移 | 弃用候选，改用记录来源的整栋实景照片进行动态排版 |
| 本次公开归档 | 上传同一份完整有声视频、核对片、源工程与复用资料 | 后续版本继续追加日期、问题、修改与核验，不抹去历史 |

### 工作流、提示词和对话

- [逐步复用与 ComfyUI 节点说明](projects/skyscraper-crisis/WORKFLOW.md)
- [23 条实际提示词、参数、失败候选与新项目总指令](projects/skyscraper-crisis/PROMPTS.md)
- [完整科普台词](projects/skyscraper-crisis/SCRIPT_FULL_V1.md)
- [78 段台词到具体画面的执行表](projects/skyscraper-crisis/full-film-v2/逐段画面执行表.md)
- [创作对话记录（可恢复的用户消息与可见回复）](projects/skyscraper-crisis/conversation/TRANSCRIPT.md)
- [迭代复盘与验收清单](projects/skyscraper-crisis/ITERATIONS.md)
- [新主题复用表](projects/skyscraper-crisis/templates/NEW-PROJECT.md)
- [资料与画面依据](projects/skyscraper-crisis/full-film-v2/资料与画面依据.md)
- [本次 Release：完整视频与重渲染素材包](https://github.com/yenicee1014/Explainer-Video-workflow/releases/tag/skyscraper-crisis-v2-2026-10-25)

![六类具体情节核对](projects/skyscraper-crisis/six-mechanisms.jpg)

---

## 持续迭代：新增《NASA 朋克》（2026-10-27）

这次从路北路陈的《设计风格小课 04》（Bilibili `BV1Tsps6kE6z`）出发，用 HTML、SVG、CSS、GSAP 和 HyperFrames 重建一支讲述 NASA 视觉系统与游戏美术的科普视频。**这是代码重建版，不是原片工程，也不是逐帧 1:1 复刻。** 天气项目与《繁荣的高度》的版本记录保持不变。

- [在线播放：完整有声视频与章节跳转](https://yenicee1014.github.io/Explainer-Video-workflow/nasa-punk.html)
- [仓库中的完整 MP4](video/nasa-punk-full-rebuild.mp4)
- [项目说明、章节与交付清单](projects/nasa-punk/README.md)
- [制作过程解析：从参考拆解到配音、动画、混音与验收](projects/nasa-punk/WORKFLOW.md)
- [源码快照与复用边界](projects/nasa-punk/source/README.md)
- [素材溯源与权利说明](projects/nasa-punk/SOURCES_AND_RIGHTS.md)

成片 **5:58.47，1280×720，30fps，H.264 + AAC**，含 14 个代码场景、67 句重新合成的普通话旁白和程序生成的配乐。旁白使用 macOS Tingting，未复用原片完整音轨；文稿、节奏和部分版式与参考作品不同。文件大小、SHA-256 及媒体规格见 [交付清单](projects/nasa-punk/delivery-manifest.json)。

### 这次是怎样做出来的

| 环节 | 实际做法 | 产物与边界 |
| --- | --- | --- |
| 拆参考 | 提取联系表、用 OCR 辅助定位章节和画面对象 | 沿用讲述脉络，不声称取得原工程或逐帧还原 |
| 建时间轴 | 逐句合成录音，检测静音，实测时长 | 67 句的局部与全局锚点；不是词级强制对齐 |
| 做讲解动作 | 字标横杠移除、比例测量、姿态旋转、截图分层标注 | 14 个独立场景；句内动作按明确相对偏移编排 |
| 做声音 | 程序合成音床、提示音和章节声标，旁白期间压低配乐 | 新配音、新配乐，非原片声音复制 |
| 验证并导出 | 先做 31 秒样段，再自动检查、导出、解码与抽帧 | 自动检查和媒体核验已完成，完整人工听看未完成 |
| 公开归档 | 发布 MP4、字幕、时间轴、源码快照和制作说明 | 不上传参考视频、素材包、字体、语音缓存或密钥 |

部分游戏、电影和服装案例静帧取自参考作品，版权仍归原权利人；个别 ARC Raiders 静帧包含参考作品已有标注。系统语音及第三方图像的公开再分发许可尚未逐项确认，**本次归档不等于授权证明或可商用素材包**。源码快照为研究与复用参考，缺少外部素材，不能开箱即用重渲染。

自动运行、布局及动作检查通过，成片完整解码无错，已检查关键帧及三段输出音轨的数值同步；另外保留了 **38 条 craft 节奏 / 设计启发式警告**（30 条静止时段、6 条文字尺寸、2 条线条阅读提示），不是“零警告”交付。**尚未完成全片正常速度人工听看、逐字校对和词级对齐**，不将自动检查描述为完整语义验收。详见 [检查范围](projects/nasa-punk/verification/README.md)。

![NASA 朋克代码重建版实际成片联系表](projects/nasa-punk/contact-sheet.jpg)
