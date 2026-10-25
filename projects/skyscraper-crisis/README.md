# 繁荣的高度：摩天大楼、现金流与经济周期

2026-10-25 · V2 情节重制版 · 8 章 / 78 段旁白 / 148 个摄影节拍。

[在线播放完整版](https://yenicee1014.github.io/Explainer-Video-workflow/skyscraper.html) ·
[完整 MP4](../../video/skyscraper-crisis-v2-full.mp4) ·
[六类经济现象核对片](../../video/skyscraper-crisis-v2-highlights.mp4) ·
[发布与素材包](https://github.com/yenicee1014/Explainer-Video-workflow/releases/tag/skyscraper-crisis-v2-2026-10-25)

这是持续迭代中的第二个主题项目。仓库原有天气项目保持原状；本项目保留从视觉试片、完整台词、V1 泛化画面到 V2 逐段情节重制的过程。**公开工作流是一份可以改造的实际制作工程，不承诺未来云服务可用性或模型逐像素复现。**

## 主题与叙事

核心问题：高楼纪录为何经常被拿来讨论经济危机？视频先校正历史先后关系，再用虚构商业地产项目解释融资与需求的错配，最后检验“摩天大楼指数”的证据。

| 章 | 起点 | 核心内容 |
| --- | --- | --- |
| 01 同一座城市，两种消息 | 00:00.00 | 帝国大厦、失业工人、银行压力；建筑高度与经济处境的反差 |
| 02 先把时间摆对 | 01:15.76 | 1929 股灾与 1930 开工；宣布、开工、封顶、营业不能混用 |
| 03 一栋楼，先在账本里建起来 | 02:09.56 | 土地、建设、出租、借款；贷款合同与租金预测的区别 |
| 04 每个人的算盘，都指向了同一个未来 | 03:43.64 | 多工地同时建设；有限租户被多个项目重复计入需求 |
| 05 楼盖的是过去，市场活在现在 | 05:10.08 | 长建设周期、企业取消扩张、实际需求收缩 |
| 06 楼没有倒，账却可能撑不住 | 06:24.32 | 租户搬离、收入下降、到期再融资、估值和信贷收紧 |
| 07 为什么这个“指数”总让人印象深刻 | 08:13.40 | 选择偏差、反例、论文与评论、样本外检验 |
| 08 真正值得看的，是哪几个问题 | 09:54.32 | 谁来使用、钱从哪来、何时到期、变差后能否承受 |

完整台词见 [SCRIPT_FULL_V1.md](SCRIPT_FULL_V1.md)。V2 沿用这份台词和配音时序；名称中的 V1 表示台词版本，不表示当前画面仍是第一版。

## 六类现象怎样上镜

| 现象 | 画面必须能看见 | 素材 ID |
| --- | --- | --- |
| 工人失业 | 工头锁门、工人提饭盒离开、银行门口排队 | `factory_close`、`bank_queue` |
| 借贷签约 | 银行递笔、开发商签字、递回合同 | `signature` |
| 工地竞争 | 四个独立工地、多楼盘模型争取少量企业租户 | `sites`、`lease_competition` |
| 租户减少 | 撤电脑、搬箱、交钥匙与空工位 | `contraction`、`departure`、`vacancy` |
| 再融资 | 旧合同与新方案并置、计算器比较、物业估值 | `refinance`、`valuation`、`credit` |
| 证据检验 | 从精选案例扩展到更多案例、先摆清单后开新资料 | `sample`、`precommit` |

![六类情节核对](six-mechanisms.jpg)

示例项目借款 6 亿元；4% 年利率对应 2400 万元利息，到期续借若为 6%，对应 3600 万元。净运营收入从 5000 万降到 3500 万后，出现相对利息的 100 万元缺口。此为虚构教学示例，未计税费与还本。旧固定利率贷款不会仅因市场加息立即改成新利率。

## 文件导航

| 路径 | 用途 |
| --- | --- |
| [WORKFLOW.md](WORKFLOW.md) | 环境、节点安装、API、按章生成、重渲染、合成与故障恢复 |
| [PROMPTS.md](PROMPTS.md) | 23 条真实采用的提示词、seed、参数和可直接改写的总指令 |
| [ITERATIONS.md](ITERATIONS.md) | 需求变化、失败原因、替换方案和验收方法 |
| [conversation/TRANSCRIPT.md](conversation/TRANSCRIPT.md) | 可恢复的创作对话，保留纠偏过程 |
| [templates/NEW-PROJECT.md](templates/NEW-PROJECT.md) | 新主题的旁白、分镜、提示词和核验模板 |
| [full-film-v2/storyboard.json](full-film-v2/storyboard.json) | 78 段旁白与有序素材 ID |
| [逐段画面执行表](full-film-v2/逐段画面执行表.md) | 同一映射的可读版本 |
| `full-film-v2/01–08/` | 各章生成 API、合成 API、timeline、字幕与核对图 |
| `full-film-v2/assets/<id>/` | 实际 brief、生成 API 图和起中末帧核对图 |
| [workflow-generation.json](full-film-v2/workflow-generation.json) | 拖入 ComfyUI 的 01→08 串行素材工作流 |
| [workflow-preview.json](full-film-v2/workflow-preview.json) | 拖入 ComfyUI 的已完成视频预览图 |
| [comfyui 节点](../../comfyui/custom_nodes/skyscraper_editorial/__init__.py) | `SCSceneBatch` 和 `SCFullChapter` 的公开实现 |
| [environment.json](environment.json) | 本次 ComfyUI 节点、第三方节点与渲染参数快照，不含账户信息 |
| [poster.jpg](poster.jpg) · [captions.vtt](captions.vtt) | 播放页封面与可选字幕轨 |
| [资料与画面依据](full-film-v2/资料与画面依据.md) | 来源、真实照片、示意与已知研究限制 |
| [delivery-manifest.json](delivery-manifest.json) | 同步视频的 SHA-256、大小和精确参数 |
| [render-assets-manifest.json](render-assets-manifest.json) | 重渲染素材包的 SHA-256 与逐文件清单 |
| `history/demo/` | 早期方案及试片工作流，带当时状态，不作为当前入口 |

## 最快复用

查看成片只需打开网页或 MP4，无需运行 ComfyUI。

重渲染现有项目需要 FFmpeg、Python 依赖、中文字体和 Release 素材包：

```sh
cd projects/skyscraper-crisis
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python reproduce.py fetch-assets
.venv/bin/python reproduce.py check
.venv/bin/python reproduce.py render --chapter 3
```

字体自动尝试本机常见位置。找不到时，设置 `SC_FONT`、`SC_SERIF_FONT`、`SC_LATIN_FONT`，见 [.env.example](.env.example)。`reproduce.py check` 不会提交任何云任务。

要从头生成，先按 [WORKFLOW.md](WORKFLOW.md) 安装 ComfyUI 节点和自己的云服务连接，再运行旁白、旧版补充素材和 V2 情境生成；不必为已经下载的素材重复付费。新主题从 [模板](templates/NEW-PROJECT.md) 开始，修改完整台词、`CHAPTERS`、`ASSETS`、`BEATS` 与数字排版，不能只替换标题或覆盖旧缓存。

## 成片与核验范围

原文件时长 **666.581333 秒 / 11:06.58**，1280×720、25fps，保留普通话旁白与字幕。本次 GitHub 同步不重编码，文件哈希与本地交付版一致。

已有制作检查记录位于 [content-audit.json](full-film-v2/content-audit.json)、各章 `verification.json` 与 [visual-review.json](full-film-v2/visual-review.json)：覆盖全片解码、旁白一致性、素材存在、章节音画时长，以及抽帧和选段人工画面审查。人工审查不等于每帧人物动作都完美，也不等于已取得论文全文。

## 许可与来源

人物经济情节标注为 AI 情境重建；中文金额、日期、字幕与论文书目由后期排版。具名建筑最终使用带来源的真实照片，未将生成轮廓错误的候选当作地标。

原始摄影及视频中的第三方影像保留来源权利。来源可追溯不等于已取得全面再分发或商业授权。TTS 使用 `edge-tts` 调用 `zh-CN-YunxiNeural`，也不构成对任何后续用途的授权保证。仓库没有为这些内容授予新的通用许可，见 [第三方说明](../../THIRD_PARTY_NOTICES.md)。素材包仅收录本片实际重渲染输入，不包含模型权重、账户设置或密钥。
