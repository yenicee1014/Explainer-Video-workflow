# ComfyUI 横屏镜头提示词

> 已暂停，勿用于下一次生成。以下提示词属于此前未根据原片核实的写实 CG 方向。参考观察见 `REFERENCE_ANALYSIS.md`，新的节点与验收方案见 `COMFY_WORKFLOW.md`。完成参考分析、原创分镜与静帧确认前，不编造替代提示词，也不提交 H3 任务。

统一风格前缀：

`16:9 horizontal documentary explainer, cinematic but restrained, realistic architectural visualization, clean editorial composition, wide negative space for post-production captions, muted charcoal and steel palette with small cyan and amber accents, controlled camera movement, original fictional city, no logos, no readable text, no real landmark, no watermark`

统一负面约束：

`no famous landmark, no reference-video recreation, no copied composition, no brand logo, no readable gibberish text, no generated subtitles, no warped buildings, no melting geometry, no duplicated windows, no extra towers appearing from nowhere, no cartoon style, no dramatic disaster spectacle, no disaster footage`

## Shot 01 - 开场

`A fictional ultra-tall skyscraper rising above a dense modern city at blue hour, wide 16:9 establishing composition with the tower placed off-center, camera starts at street level and slowly tilts upward along the facade, anonymous untextured billboards in the foreground, the tower lights briefly flicker and stabilize, distant clouds move slowly, thoughtful economic documentary mood, original architectural design, no real landmark`

## Shot 02 - 误会校正

`Wide editorial visualization of one fictional skyscraper and three abstract rising trajectories converging near its foundation, each trajectory has a distinct color and material quality, slow lateral camera move across a dark city model, clean negative space on the right for post-production labels, no readable text, no real landmark`

## Shot 03 - 便宜信贷

`Abstract but realistic horizontal financial visualization: a fictional construction site and a growing glass tower, translucent blue capital-flow ribbons enter the foundation, a simple descending curve is represented by light rather than readable numbers, slow lateral camera move, wide 16:9 composition, no readable labels`

## Shot 04 - 城市竞赛

`Three fictional city silhouettes across one wide frame gradually compete in height, construction cranes and abstract collateral documents overlap through restrained double exposure, cool steel architecture with small amber highlights, slow panoramic move, original city designs, no logos, no readable text`

## Shot 05 - 时间差

`One fictional skyscraper held in a stable wide composition through a seamless time-lapse from architectural blueprint to steel frame to completed illuminated tower, seasons and daylight change around it, the background light trajectory slowly turns upward, elegant economic documentary visualization, 16:9 horizontal`

## Shot 06 - 现金流反转

`Nighttime fictional office tower in a wide 16:9 frame with many illuminated windows, lights gradually go dark floor by floor, empty desks become visible through glass, a subtle red light trail falls across the facade, slow push-in, restrained and non-catastrophic, original architecture`

## Shot 07 - 事后观察

`Wide overhead view of a fictional city model connected to a clean physical timeline made of light blocks, stages shift from planning to construction to completion to revaluation, a translucent shadow passes over the final stage, elegant analytical mood, no readable labels, no copied infographic layout`

## Shot 08 - 结尾

`Camera descends from the roof of a fictional skyscraper through a stylized cutaway city into the underground foundation, showing steel piles, flowing water, transit lines and abstract cash-flow pulses reconnecting below street level, calm dawn light, hopeful analytical ending, wide 16:9 composition, original design`

## 音画合成约束

- AI 视频节点只生成无文字画面，字幕与数据标签在后期节点完成。
- 画面统一为 1280x720 试片，最终可切换为 1920x1080。
- 每个镜头先生成 10 秒，保留 6-8 秒可用段落。
- 后期只使用原创旁白、原创时间轴和原创三线图解。
