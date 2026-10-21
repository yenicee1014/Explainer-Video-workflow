# 天气预报 × AI：为什么还会报不准？

天气科普项目的公开工作流与版本档案。当前创作方向保留奶油白、黑色、红色强调的已确认排版，并以真实、可追溯的天气照片补足具象画面；抽象概念仍使用明确标注的原创教学图解。

> **当前版本：第一章真实照片版本地预览，并已导出无声 MP4。** 画面长约 1 分 55 秒，1080×1920，五个场景、22 条句级字幕；全稿其余章节尚未完成视觉制作。全稿约 16 分 39 秒的本地配音并不等于完整成片。公开 MP4 只含画面，不含许可尚未核实的系统女声。

## 可点击播放

- [点击播放第一章无声 MP4（GitHub 文件页）](video/weather-real-preview-chapter1-silent.mp4)
- [直接打开 MP4（Raw 文件）](https://github.com/yenicee1014/Explainer-Video-workflow/raw/main/video/weather-real-preview-chapter1-silent.mp4)

该 MP4 是第一章的竖屏画面导出：保留字幕、动画和说明文字，时长约 1 分 55 秒，视频编码为 H.264，分辨率 1080×1920，无音轨。浏览器本地预览仍保留普通话声音；完整全片和有声 MP4 尚未完成。

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
