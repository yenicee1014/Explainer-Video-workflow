# 修改与贡献规范

提交前请阅读 `README.md`、`VERIFICATION.md` 和 `THIRD_PARTY_NOTICES.md`。公开仓库当前未选定通用开源许可证；贡献前请与维护者确认使用和授权安排。

## 内容修改

1. 修改科学结论时同步资料索引、引用范围和场景注释，优先引用可核查的一手资料。
2. 同步 `script.json` 与 `timeline.json`，保持字幕文本及场景元数据一致；计时变动必须重新检查连续性。
3. 图解生成逻辑集中在 `tools/diagrams.py`；修改生成器后重新构建，不只手改生成的 SVG。
4. 不加入来源网站全文、未获许可图片、字体二进制、私人媒体、API 密钥或绝对本机路径。

## 提交检查

在仓库根目录执行：

```sh
python3 tools/build.py
python3 tools/check_content.py
python3 -m unittest discover -s tests -v
python3 tools/workflows.py
git diff --check
```

界面或动画改动还应执行浏览器检查；节点或图结构改动应在本机 ComfyUI 真实运行。报告只描述已执行的检查，明确未覆盖范围，不把自动化检查称为科学认证。

提交讲稿／代码及对应生成产物，避免提交 `node_modules`、缓存、系统元数据、声音和视频文件。未经维护者确认，不以添加 LICENSE 的方式改变现有授权边界。
