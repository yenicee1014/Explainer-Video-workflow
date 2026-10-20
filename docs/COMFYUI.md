# ComfyUI 安装与使用

## 适用范围

本仓库的公开工作流为无声字幕动画工程提供可复现构建，已在 ComfyUI 0.34.0、Python 3.13.12、CPU 环境实际执行。其他版本需自行验证。工作流不依赖模型权重、TTS、付费 API 或 GPU，也不渲染 MP4。

## 安装节点

1. 下载或克隆完整仓库，保留其目录结构。
2. 将 `comfyui/custom_nodes/explainer_public` 文件夹复制或建立符号链接到你安装的 `ComfyUI/custom_nodes/explainer_public`。
3. 在启动 ComfyUI 的同一进程环境中设置 `EXPLAINER_REPO`，值为本仓库根目录的绝对路径。复制节点后不可省略此项；路径中含空格时加引号。
4. 重启 ComfyUI。检查启动日志中该节点加载成功。

例如在 macOS／Linux，使用你的 ComfyUI Python 环境启动，临时环境变量不需要写入 shell 配置：

```sh
EXPLAINER_REPO="/absolute/path/Explainer-Video-workflow" python main.py --cpu
```

此命令在 ComfyUI 安装目录执行，`python` 应为其环境中的 Python。Windows 可在启动器或当前进程环境中设置同名变量；本仓库未实测 Windows 启动器。

节点只有 Python 标准库依赖，无额外 requirements 安装步骤。节点会读取仓库并覆盖生成的 SVG、SRT 和报告；请先保存自己的修改。

## 导入界面工作流

将 `workflows/weather-silent.json` 拖入 ComfyUI，或使用其打开工作流功能。核对有五个节点和四条连接：

1. **读取公开讲稿与冻结计时**（`EXLoad`）：工程相对路径默认为 `projects/weather-ai`。
2. **检查来源、字幕与时间线**（`EXValidate`）：校验当前 40 场景版本的数据约束。
3. **生成确定性科学图解**（`EXDiagrams`）：生成 40 幅教学 SVG。
4. **导出完整字幕**（`EXCaptions`）：按已有计时生成 `captions.srt`。
5. **生成无声审阅报告**（`EXReview`）：显示 JSON 结果并写入 `reports/build-check.json`。

点击运行后，最后节点应显示 `status: passed`、`scenes: 40`、`captions: 167` 和 `audio: false`。产物写入本仓库，不在 ComfyUI 常规图片输出目录。

随后从**仓库根目录**启动 `python3 -m http.server 3033 --bind 127.0.0.1`，打开 <http://127.0.0.1:3033/projects/weather-ai/> 查看动画。

## API 验证

`weather-silent-api.json` 是 API 图，和界面图用途不同。已安装节点且本地 ComfyUI 运行后，在仓库根目录执行：

```sh
python3 tools/check_comfy.py --url http://127.0.0.1:8190
```

将端口改成实际本机端口，例如默认 8188。脚本会真实提交一次工作流、等待完成、核验最终节点结果，并写入 `reports/comfy-check.json`。只支持本机 HTTP 地址，无需凭证，不调用云服务。

## 编辑约束与排错

- 当前发布固定为 40 场景；不是任意场景数的通用模板。扩展场景数需同步修改验证规则和测试。
- `script.json` 与 `timeline.json` 中的场景文案、标签、来源等必须一致；字幕拼接必须等于对应讲稿。更换旁白后需自行制作并核验新计时，工作流不会自动对齐音频。
- `sources.json` 的 `verified` 是内容研究记录，不是运行时联网核实结果。
- 缺节点：核对文件夹名称、启动日志及是否重启；五个节点归类于 `Explainer / Silent review`。
- 提示设置 `EXPLAINER_REPO`：核对变量是否传入 ComfyUI 进程，且目标根目录含 `tools/build.py`。
- 校验失败：先读错误字段并同步讲稿、时间线和字幕；不要用 Python `-O` 绕过断言，构建程序会拒绝该模式。
- 写入失败：确认仓库可写。建议先备份，不以管理员权限掩盖权限问题。
- 本地验证曾出现 ComfyUI 数据库初始化警告，但 HTTP 和工作流成功；不据此保证其他数据库或插件功能正常。
