---
name: living-still
description: Turn an uploaded ordinary static photo into a hand-drawn illustration (default Franco-Belgian ink-hatching style) where the whole scene stays frozen except ONE randomly chosen, contextually fitting element that comes alive in place (stylized cinemagraph / 静图微动). Deliver a looping 3:4 MP4 ready for Xiaohongshu, Instagram, TikTok, and WeChat Channels, plus an Apple Live Photo JPEG/MOV pair when running on macOS. Use when the user uploads a photo and asks to 让照片动起来/让一个元素动起来/做成动图/GIF/Live Photo/实况照片/cinemagraph/静中有动/活过来, or wants a creative stylized living illustration of a real-life scene. Triggers on "把这张照片做成动图", "做成Live图", "做成实况照片", "随机让一个东西动起来", "living still", "cinemagraph".
---

# Living Still 静中有动

把用户的普通照片变成一张手绘插画动图（签名风格配方见 [references/style-guide.md](references/style-guide.md)，当前默认为法式漫画影线风）：**全画面静止，只有一个随机选中的元素原地动起来**，循环播放。

## 前置

### 照片方向校正（EXIF，第一步必做）

手机照片的旋转信息存在 EXIF 里，直接压缩上传会把"侧躺"的像素喂给生成器，构图跟着斜倒。拿到照片先校正再压缩：

```python
from PIL import Image, ImageOps
im = ImageOps.exif_transpose(Image.open(photo_path))  # 应用 EXIF 旋转
im.thumbnail((1200, 1200))                            # 压缩防大图 400
im.convert('RGB').save('/tmp/ref.jpg', quality=88)    # 另存顺带剥掉 EXIF
```

**画幅铁律**：无论原片横竖方圆，输出永远**竖版 3:4**。Kimi 的 image_generation 插件用 `--size "960x1280"` 直接生成 3:4（该插件指定像素尺寸，没有 --ratio/--resolution 参数）；不支持自定尺寸的平台按 `2:3` 生成、提示词要求竖版构图并给主体四周留余量，由 `make_gif.py --aspect 3:4` 居中裁切兜底。禁止输出其他画幅。

### 依赖结构（跨平台说明）

1. **图像生成层**：需要支持参考图（图生图）的文生图工具。在 Kimi 里用 `image_generation` 插件（插件根目录运行 `scripts/image_generation_tool.py`，先跑 `ensure-deps`）；在其他 LLM 平台用其自带的图生图能力（DALL·E、Stable Diffusion、Gemini 图像等）——本技能的提示词配方与平台无关，直接照搬。用户照片与基准帧必须先转成公开 URL 再作为参考图传入（Kimi 用 `image-to-url`，其他平台用各自图床），**不可省略**——帧间一致性全靠它。
2. **合成与 Live Photo 打包层**：`scripts/make_gif.py` 是纯 Python 3 + Pillow 脚本，负责导出各平台直接上传的 MP4。`scripts/make_live_photo.py` 在 macOS 上调用 `ffmpeg` 与开源的 `makelive`，后者使用 Apple 原生框架写入真正的 Live Photo 配对元数据；Windows/Linux 不尝试伪造 Live Photo，仍可完整产出 MP4。

### 生成不稳定时的处理

文生图服务偶发超时/限流。失败后先检查输出文件是否已落盘；没有就以相同参数原样重试，最多 2-3 次；仍失败照实告诉用户，不要编造图片。

## 工作流程（六步）

### 第 1 步：读照片，列候选元素

仔细看照片：场景类型、主体、所有**可能原地运动**的元素。列出 3-6 个候选，按 [references/animation-playbook.md](references/animation-playbook.md) 的规则筛选：

- **只能原地动**：元素位置、大小基本不变，只做局部形态/状态变化（火苗跳动、蒸汽飘、灯光闪烁、窗帘轻摆、水面涟漪、尾巴摇晃）。
- **不选**：人脸/眼睛（容易诡异）、需要位移的元素（走动的人、开走的车）、画面主主体的大动作。
- 候选必须**符合情景**：厨房里选火苗/蒸汽/水龙头滴水，不选与场景无关的东西。

### 第 2 步：真随机抽签

把候选元素传给脚本，由 `SystemRandom` 真随机抽一个，不要自己"挑一个顺眼的"：

```bash
python3 scripts/pick_random.py 火苗 蒸汽 窗帘 挂钟摆锤
```

抽到哪个就用哪个。抽中的元素如果不幸违反规则（极个别情况），按原候选列表重抽一次并向用户说明。

### 第 3 步：生成基准帧（全静态风格图）

读 [references/style-guide.md](references/style-guide.md) 拿签名风格配方，组英文提示词：**照片内容忠实描述 + 配方句 + "everything perfectly still, frozen moment" 收尾**。照片内容必须写全（主体、位置、颜色、光线），不能只靠参考图。画幅按上方铁律选 `2:3` 或 `1:1`，提示词加 "vertical composition with margin around the subject" 为 3:4 裁切留余量。带原照片 URL 作为参考图生成基准帧 `frame1.png`。

### 第 4 步：生成动画帧（只动一个元素）

以**基准帧的 URL 作为参考图**（不是原照片！），逐帧生成 `frame2.png`、`frame3.png`、`frame4.png`，提示词模板：

```
[基准帧完整描述], IDENTICAL composition, colors and style to the reference image, 
everything remains perfectly frozen and unchanged, ONLY the [抽中元素] changes: [该帧的运动状态描述]
```

三帧分别描述元素运动的**开始→高峰→回落**三个阶段（如火焰：点燃初燃→窜高跳动→压低回稳）。每帧除该元素外必须与基准帧逐像素级一致。若某帧偏差太大（其他元素也变了），重生成该帧。

### 第 5 步：合成用于社交平台上传的循环短片（MP4）

```bash
python3 scripts/make_gif.py \
  --frames frame1.png frame2.png frame3.png frame4.png \
  --fps 5 --pingpong --aspect 3:4 \
  --output 主题-静中有动.mp4
```

**默认交付 MP4，不出 GIF 也不出静态图**：GIF 在很多手机相册和社交平台（微信、小红书、Instagram）会被压成静态首帧，MP4 短视频全平台原生可动、自动循环。脚本会把 1-2-3-4-3-2 往返序列自动重复到约 4 秒，H.264 编码。

**去水印（默认开启）**：图像生成器会在每一帧左下角打半透明「AI生成」字样。`make_gif.py` 默认先把每个源帧底部 7% 裁掉再合成（`--crop-bottom`，默认 0.07；水印只出现在这个角落，且提示词已要求主体四周留余量，裁掉最干净，置 0 可关闭）。因此最终输出约 892×1190，仍是标准 3:4。

- MP4 编码优先用 `imageio-ffmpeg`（自带 ffmpeg 二进制，跨平台免装系统依赖：`pip install imageio-ffmpeg`），没装则回退到系统 `ffmpeg`；两者都没有时脚本报错并提示安装。
- 火焰/蒸汽类快节奏用 `--fps 6`，灯光闪烁/窗帘类慢节奏用 `--fps 3`。
- 用户明确要 GIF 才把 `--output` 改成 `.gif`；明确要静态图才加 `--still 主题.png`。

### 第 6 步：打包 Apple Live Photo（默认）

MP4 是小红书、抖音、Instagram、TikTok、微信视频号等平台最稳定的动图上传格式；不要把 GIF 当成默认交付。为了让用户也能在 iPhone 相册里得到真正的“实况照片”，用第 5 步生成的 MP4 与首帧额外打包为 Apple Live Photo 配对资源：

```bash
python3 scripts/make_live_photo.py \
  --photo frame1.png \
  --video 主题-静中有动.mp4 \
  --output-dir 主题-LivePhoto
```

这个目录会生成同一资产标识符的 `.JPG` 和 `.MOV`，并附带说明文件。两者必须一起导入 iPhone/macOS 的“照片”应用，才能显示为一张可长按播放的 Live Photo。不能把 MP4 重命名为 `.live`、`.gif` 或 `.jpg` 冒充 Live Photo。

- `ffmpeg` 负责将视频封装成兼容的 H.264 MOV；`makelive` 使用 macOS 的 Core Graphics 与 AV Foundation 写入 JPEG/MOV 的配对元数据。它只能在 macOS 上运行；Windows/Linux 环境直接交付第 5 步 MP4，并明确说明 Apple Live Photo 打包不可用的原因。
- 所有目标平台均同时交付 `主题-静中有动.mp4`。用户要发小红书等社交媒体时，优先上传这个 MP4；它会作为一个 3:4 的短视频正常播放。
- Apple Live Photo 是相册格式，并不是所有社交平台的上传格式。用户指定“实况照片”“Live Photo”或使用 iPhone 时，才额外交付 `主题-LivePhoto` 文件夹中的配对资源。

## 交付

- 默认交付 `主题-静中有动.mp4`，这是小红书等平台的直接上传文件；展示给用户并用一句话揭晓“这次抽中的是××”。
- 在 macOS 上，同时交付 `主题-LivePhoto` 中的 `.JPG`、`.MOV` 和 `README.txt`，用户把两个媒体文件一起导入“照片”应用后可作为真正的 Live Photo 播放。Windows/Linux 则清楚说明该格式需要 macOS 打包，不把普通 JPG/MOV 冒充 Live Photo。
- 用户想换元素：不重生成基准帧，直接从第 2 步重抽（或按用户指定元素）出帧再合成。
- 用户明确要 GIF / 静态图时才按第 5 步的可选参数补出，默认不给。
- 交付文件名用中文（如 `厨房-静中有动.mp4`）；提示词一律英文。

## 注意

- 动画元素只有一个，禁止两个以上元素同时动——"全静一点动"的对比感是这个技能的全部魅力。
- 帧间一致性是最大风险：动画帧必须以基准帧为参考图，提示词里反复强调 "everything else perfectly frozen"。
- 生成失败照实说原因，不要编造图片或路径。
