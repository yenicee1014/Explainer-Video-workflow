# 实际使用的提示词与复用模板

本文件以 `full-film-v2/asset-plan.json` 和已保存的 ComfyUI API 图为准。
23 条为采用的经济机制镜头；历史 demo 和被弃用建筑候选单独归档。

## 从文字到镜头的模板

```text
主题：[要解释的经济现象]
旁白：[这一段完整旁白]
必须看见：[人物/物件]在[环境]做[可以观察到的动作]
因果关系：[动作怎样解释旁白，而不是只画同一栋楼]
统一风格：黑白纪实摄影、灰白纸纹、暗红重点、16:9
模型只生成：无字人物/物件/环境/动作镜头
后期准确排版：金额、利率、日期、字幕、来源与示意标签
验收：[开始/中间/结束帧中必须看见的动作]
```

## 本次实际模型参数

- ComfyUI 节点：`AutoDLWorkflow` → `AutoDLPreviewVideo`。
- 云工作流：`minimax_h3_lightx2v_no_pic`；历史 schema version 6。
- 片长：每条 8 秒；分辨率槽位：`768p横`。
- seed：`2026102500 + sum((i + 1) * ord(c) for i, c in enumerate(asset_id))`。
- 本次素材经后期合成为 1280×720、25fps，不能把云端枚举写成 `1280x720`。
- 没有独立 negative prompt 槽位，排除要求写入总提示词。
- 云目录、可用模型和收费可能变化；复用前核对你自己的账户。

## 23 条采用的镜头提示词

### 01 / factory_close / 工厂停工与离岗

seed：`2026112288`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/factory_close/workflow-api.json) · [三帧核对图](full-film-v2/assets/factory_close/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium wide shot outside a small American factory in 1931. A foreman in a wool coat locks the factory's iron gate. Three dismissed manual workers, wearing flat caps and worn jackets, pick up their lunch pails and walk away slowly. Smoke stacks are idle. Period correct clothing and street, no modern cars. The closed gate and workers leaving are both clearly visible.
```

### 01 / bank_queue / 储户排队与银行压力

seed：`2026108393`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/bank_queue/workflow-api.json) · [三帧核对图](full-film-v2/assets/bank_queue/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Wide street-level shot of a modest American bank entrance in 1931. A long orderly queue of ordinary depositors in period coats waits outside heavy stone doors. A bank employee quietly speaks to the first person in line. Natural worried faces. The queue bends along the bank facade, no violence, no readable signs.
```

### 02 / exchange / 1929年交易所内的混乱

seed：`2026106228`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/exchange/workflow-api.json) · [三帧核对图](full-film-v2/assets/exchange/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. High angle medium wide shot inside a 1929 American stock exchange. Floor brokers in dark suits hurry between wooden trading desks while one broker studies a long ticker tape and another holds his head in his hands. Period correct telephones and paper. No digital screens, no modern equipment, no readable text.
```

### 03 / planning / 开发商评估办公楼计划

seed：`2026106333`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/planning/workflow-api.json) · [三帧核对图](full-film-v2/assets/planning/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Over-the-shoulder medium shot of two contemporary East Asian property developers at a plain planning table. They spread a large architectural floor plan beside a scale model of an ordinary twelve-storey rectangular office building and a calculator. One points at the land parcel and the other makes budget notes. Architectural plans and people dominate, not a skyscraper.
```

### 03 / budget / 土地、建造与运营成本

seed：`2026104745`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/budget/workflow-api.json) · [三帧核对图](full-film-v2/assets/budget/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Close tabletop documentary shot of an East Asian property finance analyst's hands sorting three folders beside a calculator, a small ordinary office building model, a construction material sample and a site plan. She calculates on the calculator, then checks a folder. Blank or indistinct document text, no readable numbers. Keep hands and objects stable and realistic.
```

### 03 / signature / 银行借贷签约特写

seed：`2026107395`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/signature/workflow-api.json) · [三帧核对图](full-film-v2/assets/signature/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Close shot at an ordinary contemporary bank desk. An East Asian male property developer in a dark jacket receives a pen from a female loan officer, signs a single page of a thick loan contract and slides it back to her. Loan officer checks the signature. Faces partly visible above desk, natural anatomically correct hands. Paper contract and signing action are the main subject.
```

### 03 / tenant_visit / 潜在租户实地看办公室

seed：`2026111033`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/tenant_visit/workflow-api.json) · [三帧核对图](full-film-v2/assets/tenant_visit/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Wide interior shot in a contemporary ordinary office floor with rectangular windows. An East Asian letting agent holds a lease folder and shows the space to two potential business tenants. One tenant checks where desks could go and the other examines the floor plan. The agent points to the usable floor area. No luxury penthouse, no exterior tower shot.
```

### 03 / growth / 企业扩张与新增工位

seed：`2026104844`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/growth/workflow-api.json) · [三帧核对图](full-film-v2/assets/growth/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium wide shot in a busy contemporary East Asian company office. A manager welcomes two new employees and points to newly installed desks. Existing staff work in the background and a technician finishes placing an office chair. Ordinary corporate workplace, confident practical business activity.
```

### 04 / sites / 多家开发商同时开工

seed：`2026104152`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/sites/workflow-api.json) · [三帧核对图](full-film-v2/assets/sites/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Elevated wide shot across four adjacent independent commercial construction sites in an East Asian city. Four different mid-rise concrete office buildings at different stages, each with its own tower crane and temporary perimeter. Cranes move slowly and concrete trucks enter different gates. Show clearly separate projects competing in the same district, no single landmark.
```

### 04 / lease_competition / 多栋新楼争取同一批租户

seed：`2026119031`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/lease_competition/workflow-api.json) · [三帧核对图](full-film-v2/assets/lease_competition/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium wide shot in a commercial office leasing showroom. Three distinct East Asian property agents each stand beside a separate ordinary office building scale model. Only two potential corporate tenants stand together in front, comparing the competing brochures. The agents gesture toward their own models. Show limited tenants and multiple separate offers.
```

### 04 / tourism / 地标观光的实际使用

seed：`2026105623`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/tourism/workflow-api.json) · [三帧核对图](full-film-v2/assets/tourism/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Wide shot on an enclosed high-rise observation deck in a modern Asian city. A handful of ordinary visitors use binoculars, photograph the skyline and walk along the glass railing. Clear practical tourist activity in a public observation deck, daylight, no recognizable brand, no dramatic stunt.
```

### 04 / investors / 开发商、贷款人与投资者的共同预期

seed：`2026107578`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/investors/workflow-api.json) · [三帧核对图](full-film-v2/assets/investors/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium wide shot around a contemporary boardroom table. Three East Asian professionals, a property developer, a bank credit officer and a private investor, review one ordinary office project model, a valuation folder and a financial forecast. Each points to a different document and nods. The same set of assumptions is being shared across the table.
```

### 05 / cancel_order / 企业取消扩张订单

seed：`2026110730`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/cancel_order/workflow-api.json) · [三帧核对图](full-film-v2/assets/cancel_order/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium close shot in a contemporary small company office. An East Asian business manager ends a phone call, removes an expansion floor plan from the active folder and places it in a closed folder. A stack of unopened office equipment boxes stands behind her. A quiet decision to postpone an office expansion, no dramatic acting.
```

### 05 / contraction / 企业收缩办公面积

seed：`2026109653`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/contraction/workflow-api.json) · [三帧核对图](full-film-v2/assets/contraction/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Wide shot of an East Asian company's office being downsized. Workers unplug several computers and stack empty chairs while a manager compares a smaller floor plan with the existing office. Half the room is already unused and staff continue working in a smaller area. No factory setting.
```

### 06 / departure / 租户搬走

seed：`2026107432`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/departure/workflow-api.json) · [三帧核对图](full-film-v2/assets/departure/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium wide shot in a contemporary office corridor. Two East Asian employees carry cardboard boxes of desk belongings out of a leased office while a property manager watches and receives a key from the last tenant. Through the open door, rows of empty desks are visible. Tenant departure, boxes, key handover and vacant space are all legible.
```

### 06 / vacancy / 空置楼层与租金让步

seed：`2026105488`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/vacancy/workflow-api.json) · [三帧核对图](full-film-v2/assets/vacancy/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Slow lateral wide shot across a nearly empty contemporary office floor. Many unoccupied desk positions and disconnected monitors. At one side an East Asian property manager shows a revised lease folder to a prospective tenant, who considers it but hesitates. Broad daylight, vacancy rather than ruined or collapsed architecture.
```

### 06 / refinance / 到期贷款的再融资谈判

seed：`2026107145`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/refinance/workflow-api.json) · [三帧核对图](full-film-v2/assets/refinance/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium shot in a bank meeting room. An East Asian developer brings an old loan folder to a female bank credit officer. She sets a new loan proposal next to the old contract and points at its repayment schedule. The developer compares the two pages with a calculator and looks concerned. Show old contract versus new proposal clearly as two folders.
```

### 06 / valuation / 物业估值重估

seed：`2026107398`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/valuation/workflow-api.json) · [三帧核对图](full-film-v2/assets/valuation/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium wide shot of a contemporary property appraiser and a bank surveyor inspecting an underoccupied office floor. One measures floor space with a handheld laser device, while the other compares rental records and photographs empty units for a valuation report. Practical inspection of usable property, no construction damage.
```

### 06 / credit / 贷款收紧传给其他企业

seed：`2026104751`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/credit/workflow-api.json) · [三帧核对图](full-film-v2/assets/credit/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium shot at a contemporary small-business loan interview. An East Asian workshop owner in work clothes brings an equipment purchase folder. The bank loan officer closes the application folder, pauses, and slides it back while the owner listens with concern. Restrained business conversation. Ordinary bank desk, no money raining.
```

### 07 / sample / 把成功与失败案例一起检查

seed：`2026104730`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/sample/workflow-api.json) · [三帧核对图](full-film-v2/assets/sample/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. High angle shot over an economic researcher's large worktable. An East Asian female researcher starts with two selected architectural photo clippings, then pulls a wider stack of case files into view and lays them out in a complete grid. Other building photographs, calendars and printed data sheets are present. Show the sample expanding from selected anecdotes to many cases, no readable text.
```

### 07 / precommit / 先定标准，再检验新数据

seed：`2026107395`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/precommit/workflow-api.json) · [三帧核对图](full-film-v2/assets/precommit/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium shot of two East Asian economic researchers at a desk. They agree on a short checklist, place it visibly at the side, then open a sealed folder containing additional case records and compare the new records with the checklist. Printed sheets contain only indistinct markings. Methodical testing, no fabricated readable charts.
```

### 08 / stress / 用更低租金和更高利息检查计划

seed：`2026104858`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/stress/workflow-api.json) · [三帧核对图](full-film-v2/assets/stress/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Medium close shot of an East Asian property financial reviewer at a desk with a calculator, a lease folder and a loan contract. She sets optimistic forecasts aside, calculates an alternative budget, and points to a shortfall on the new sheet while a developer listens. Calm analytical work, no readable paper text or screen text.
```

### 08 / ledger / 核对账本与下一笔到期日

seed：`2026104711`；时长：8 秒。
[实际 API 工作流](full-film-v2/assets/ledger/workflow-api.json) · [三帧核对图](full-film-v2/assets/ledger/contact.jpg)

```text
Black-and-white observational documentary footage for a serious economics explainer. Neutral grayscale silver-gelatin photography, detailed faces and material textures, soft daylight, moderate contrast, clear readable composition. Original illustrative reconstruction. Natural restrained gestures, physically coherent objects and hands. Landscape 16:9. One continuous shot, gentle camera movement only. No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. Close overhead shot of a contemporary accountant's hands comparing a rental ledger, an ordinary paper calendar and a loan repayment schedule on a textured desk. She circles one calendar cell, checks it against the contract, then presses a calculator key. Papers have indistinct writing, the exact labels will be added in post-production.
```

## 早期提示词与失败候选

第一版每章只用一条泛化素材，无法充分表现段内台词。八条原提示词保存在 `full-film/01–08/storyboard.json` 的 `generation_prompt` 字段。
早期 demo 的探索提示词在 `history/demo/`，其中 `PROMPTS.md` 明确标为暂停使用。
它们说明迭代过程，不能代替上面的最终镜头库。

`esb_motion`、`burj_motion` 的生成建筑候选因轮廓失真被弃用。其 brief/API/核对图保留在对应资产目录；成片改用带来源的实景照片。
最终 `Media.path()` 将这些名字映射至照片，名字不代表采用了失败视频。

## 下一次项目的可直接粘贴总指令

```text
请制作一个关于[主题]的原创科普视频，先研究事实与参考片的一般视觉语言。
先写完整旁白，再按章节把每段台词拆成可见主体、动作和物件。
为每段列出必须看见的证据，再编写生成提示词；不能整章重复同一张通用素材。
先检索真实建筑、设备和历史照片，记录来源、日期、用途及许可状态。
可用AI重建经济机制，但必须标注示意，真实地标保持准确轮廓。
所有中文字、日期和金额在后期排版，不依赖生成模型的纸面文字。
按01–08顺序生成，每条只安排一个清楚动作，先查看起中末帧，再进入合成。
保持灰白纸纹、黑白摄影、暗红标注的统一设计框架。
先交付六类关键现象核对片，再合成全片；检查旁白不变、时序、金额、音画时长和完整解码。
保留旧版，记录失败原因与替换方案，导出所有工作流、提示词、字幕、来源和版本说明。
```
