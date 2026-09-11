<h1 align="center">Living Still · 静中有动</h1>

<p align="center">
  <strong>一张照片，只让一个元素悄悄活起来。</strong><br>
  Turn a still photo into a hand-drawn cinemagraph where exactly one natural element comes alive.
</p>

---

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-087ea4">
  <img alt="Works with Codex, Kimi and other agents" src="https://img.shields.io/badge/Works_with-Codex_%7C_Kimi_%7C_Other_Agents-5a9f0b">
  <img alt="Outputs MP4, GIF and Live Photo" src="https://img.shields.io/badge/Outputs-MP4_%7C_GIF_%7C_Live_Photo-087ea4">
  <img alt="Language: Chinese" src="https://img.shields.io/badge/Language-%E4%B8%AD%E6%96%87-d04449">
</p>

---

`living-still` 是一个可复用的 AI Skill，包含完整的创作流程、动画元素选择规则、风格提示词，以及用于生成 MP4、GIF 和 Apple Live Photo 配对资源的辅助脚本。默认输出为适合小红书、Instagram、TikTok 和微信视频号的竖版 3:4 MP4。

## 特性

- **全静一点动**：全画面冻结，只允许一个元素原地微动。
- **自然场景逻辑**：优先选择火焰、蒸汽、窗帘、水面、灯光、落叶等符合现实因果的元素。
- **真随机选择**：使用 `SystemRandom` 从合格候选中抽取动画元素。
- **统一视觉风格**：默认采用法式漫画墨线、交叉影线和孔版印刷颗粒风格，也提供多种可选风格。
- **社交平台优先**：默认合成约 4 秒的 H.264 MP4，可选 GIF 和静态首帧。
- **Live Photo 支持**：在 macOS 上可额外生成带正确配对元数据的 JPEG/MOV 资源。

## 工作原理

```text
原始照片
   ↓ EXIF 方向校正
候选动画元素 → 随机抽取一个
   ↓
生成手绘基准帧（全部静止）
   ↓ 以基准帧作为参考图
生成 3 个动画阶段帧（只改变选中元素）
   ↓
1-2-3-4-3-2 乒乓循环
   ├─ MP4 / GIF
   └─ Apple Live Photo（仅 macOS）
```

图像生成由运行该 Skill 的 AI 平台完成；仓库中的 Python 脚本负责随机选择、画幅归一化、循环合成和 Live Photo 打包，不包含图像生成模型。

## 目录结构

```text
living-still/
├── SKILL.md
├── README.md
├── references/
│   ├── animation-playbook.md
│   └── style-guide.md
└── scripts/
    ├── make_gif.py
    ├── make_live_photo.py
    └── pick_random.py
```

- `SKILL.md`：Skill 的入口、触发条件和完整工作流。
- `references/style-guide.md`：默认视觉配方与风格变体。
- `references/animation-playbook.md`：动画元素筛选和逐帧状态写法。
- `scripts/pick_random.py`：从候选元素中安全随机抽取一个。
- `scripts/make_gif.py`：合成 MP4、GIF，并可导出静态首帧。
- `scripts/make_live_photo.py`：在 macOS 上生成 Apple Live Photo 配对资源。

## 环境要求

- Python 3.9+
- [Pillow](https://pillow.readthedocs.io/)
- MP4 输出需要以下任一项：
  - `imageio-ffmpeg`（推荐，附带 ffmpeg 可执行文件）
  - 系统已安装并可从 `PATH` 调用的 `ffmpeg`
- Apple Live Photo 额外要求：
  - macOS
  - `ffmpeg`
  - 可从 `PATH` 调用的 `makelive`
- 一个支持参考图或图生图的图像生成工具

安装 Python 依赖：

```bash
python -m pip install Pillow imageio-ffmpeg
```

## 安装 Skill

克隆或下载仓库，然后进入项目目录：

```bash
cd living-still
```

将整个 `living-still` 目录放入所用 AI Agent 的 Skill 目录，并确保 `SKILL.md` 位于目录根部。不同运行环境的 Skill 目录位置可能不同，请以对应产品的说明为准。

如果通过 OpenAI Skills API 管理 Skill，可以上传整个目录或 ZIP 文件；参见 [OpenAI Create Skill API](https://developers.openai.com/api/reference/python/resources/skills/methods/create)。

## 使用方式

安装并启用 Skill 后，上传一张照片并直接描述目标，例如：

```text
把这张照片做成静中有动的短片。
```

```text
随机让画面里的一个东西动起来，输出适合小红书的版本。
```

```text
让咖啡热气轻轻动起来，并额外给我 GIF。
```

完整的代理工作流和提示词规范见 [`SKILL.md`](SKILL.md)。

## 单独使用脚本

### 1. 随机选择动画元素

至少传入两个候选项：

```bash
python scripts/pick_random.py 火苗 蒸汽 窗帘 挂钟摆锤
```

脚本只向标准输出打印抽中的元素，便于在其他工作流中调用。

### 2. 合成 MP4

```bash
python scripts/make_gif.py \
  --frames frame1.png frame2.png frame3.png frame4.png \
  --fps 5 \
  --pingpong \
  --aspect 3:4 \
  --output scene-living-still.mp4
```

常用参数：

| 参数 | 作用 | 默认值 |
| --- | --- | --- |
| `--fps` | 播放帧率 | `5` |
| `--pingpong` | 使用往返序列，减少循环接缝 | 关闭 |
| `--aspect` | 居中裁切到目标画幅，如 `3:4` | 跟随首帧 |
| `--duration` | MP4 目标时长（秒） | `4` |
| `--max-width` | 最大输出宽度 | `1080` |
| `--crop-bottom` | 裁掉底部的高度比例 | `0.07` |
| `--still` | 额外导出处理后的首帧 | 不导出 |

默认会裁掉源帧底部 7%。如果素材底部包含重要内容，或无需移除生成器标记，请显式关闭：

```bash
python scripts/make_gif.py \
  --frames frame1.png frame2.png frame3.png frame4.png \
  --pingpong --aspect 3:4 --crop-bottom 0 \
  --output scene.mp4
```

请确保对素材和任何标记的处理符合所用生成服务及发布平台的条款。

### 3. 输出 GIF 或静态首帧

```bash
python scripts/make_gif.py \
  --frames frame1.png frame2.png frame3.png frame4.png \
  --fps 5 --pingpong --aspect 3:4 \
  --still cover.png \
  --output scene.gif
```

### 4. 打包 Apple Live Photo

此步骤只能在 macOS 上运行：

```bash
python scripts/make_live_photo.py \
  --photo frame1.png \
  --video scene-living-still.mp4 \
  --output-dir scene-LivePhoto
```

输出目录包含同一资产标识符对应的 `.JPG` 和 `.MOV`。将两个文件一起导入 Apple“照片”应用，才能保留 Live Photo 配对关系。普通 JPG/MOV 改后缀不能替代该元数据。

## 输出格式

| 格式 | 推荐用途 | 说明 |
| --- | --- | --- |
| MP4 | 小红书、Instagram、TikTok、微信视频号 | 默认交付，兼容性最好 |
| GIF | 文档、网页或明确需要 GIF 的场景 | 部分相册和平台可能只显示首帧 |
| PNG | 封面或静态版本 | 使用 `--still` 额外导出 |
| Live Photo JPEG/MOV | iPhone 与 macOS“照片” | 仅可在 macOS 正确打包 |

## 已知限制

- 帧间一致性取决于图像生成工具；若其他区域发生变化，需要重生成对应动画帧。
- 外部图像生成服务可能要求上传照片或生成公开参考图 URL，请先确认其隐私和数据保留政策，不要上传敏感照片。
- Live Photo 打包依赖 Apple 原生框架，因此 Windows 和 Linux 只能输出 MP4/GIF。
- `--crop-bottom 0.07` 会永久裁掉约 7% 的底部画面，使用前应检查构图。
- 当前没有锁定依赖版本，也没有自动化测试或 CI；发布稳定版本前建议补充。

## 发布前自检

```bash
python -m compileall scripts
python scripts/pick_random.py 火苗 蒸汽 窗帘
python scripts/make_gif.py --help
python scripts/make_live_photo.py --help
```

建议再使用 4 张尺寸一致的测试帧分别验证 GIF 和 MP4 输出，并在 macOS 上单独验证 Live Photo 导入。

## 许可协议

本项目采用 [MIT License](LICENSE)，Copyright © 2026 mini-fish。你可以在许可证条款允许的范围内使用、复制、修改和分发本项目。

## 贡献

欢迎提交 Issue 或 Pull Request，尤其是以下方向：

- 更多场景的自然微动模板
- 更稳定的帧间一致性策略
- 参数校验和更清晰的编码错误输出
- 自动化测试与跨平台 CI
