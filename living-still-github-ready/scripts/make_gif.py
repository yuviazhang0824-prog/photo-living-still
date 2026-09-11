#!/usr/bin/env python3
"""把动画帧合成循环短片（MP4）或 GIF。

用法:
  python3 make_gif.py --frames f1.png f2.png f3.png f4.png \
      --fps 5 --pingpong --aspect 3:4 --output out.mp4

--pingpong 生成 1-2-3-4-3-2 往返序列，首尾无缝循环。
--aspect 3:4 把所有帧居中裁成指定画幅（生成工具不支持 3:4 时靠它兜底）。
--crop-bottom 默认裁掉源帧底部 7%：生成器会把「AI生成」水印打在左下角，直接裁掉最干净（置 0 关闭）。
--still 额外输出裁好的首帧静态图（用户明确要静态版时才用）。
--output 后缀决定格式：.mp4（默认交付，社交平台都能动）或 .gif。
MP4 会自动把往返序列重复到约 4 秒，H.264 编码；
优先用 imageio-ffmpeg 自带的 ffmpeg，没有则回退系统 ffmpeg。
所有帧统一缩放裁切到同一目标尺寸，保持内容不变形。
"""
import argparse
import math
from PIL import Image


def normalize(frame: Image.Image, size: tuple) -> Image.Image:
    """缩放并居中裁剪到目标尺寸，保持内容不变形。"""
    frame = frame.convert("RGB")
    tw, th = size
    fw, fh = frame.size
    scale = max(tw / fw, th / fh)
    frame = frame.resize((round(fw * scale), round(fh * scale)), Image.LANCZOS)
    left = (frame.width - tw) // 2
    top = (frame.height - th) // 2
    return frame.crop((left, top, left + tw, top + th))


def load_frame(path: str, crop_bottom: float) -> Image.Image:
    """读帧并裁掉底部一条（生成器会把「AI生成」水印打在左下角，裁掉最干净）。"""
    frame = Image.open(path)
    if crop_bottom > 0:
        frame = frame.crop((0, 0, frame.width, round(frame.height * (1 - crop_bottom))))
    return frame


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", nargs="+", required=True, help="帧图片，按播放顺序")
    ap.add_argument("--fps", type=float, default=5.0, help="播放帧率（默认 5）")
    ap.add_argument("--pingpong", action="store_true", help="往返循环，首尾无缝")
    ap.add_argument("--aspect", default=None, help="目标画幅，如 3:4；居中裁切，默认跟首帧")
    ap.add_argument("--still", default=None, help="额外保存首帧静态图到此路径（.png），默认不出")
    ap.add_argument("--max-width", type=int, default=1080, help="最大宽度（默认 1080，适合社交平台竖版上传）")
    ap.add_argument("--duration", type=float, default=4.0, help="MP4 目标时长秒数（默认 4，往返序列自动重复凑够）")
    ap.add_argument("--crop-bottom", type=float, default=0.07, help="裁掉源帧底部这一比例高度（默认 0.07，去除左下角「AI生成」水印；置 0 关闭）")
    ap.add_argument("--output", required=True, help="输出路径，.mp4 或 .gif")
    args = ap.parse_args()

    if len(args.frames) < 2:
        ap.error("至少需要 2 帧")

    base = load_frame(args.frames[0], args.crop_bottom)
    bw, bh = base.size
    if args.aspect:
        aw, ah = (int(x) for x in args.aspect.split(":"))
        # 在首帧内取满足目标画幅的最大居中区域
        if bw / bh > aw / ah:
            w, h = round(bh * aw / ah), bh
        else:
            w, h = bw, round(bw * ah / aw)
    else:
        w, h = bw, bh
    if w > args.max_width:
        h = round(h * args.max_width / w)
        w = args.max_width

    frames = [normalize(load_frame(p, args.crop_bottom), (w, h)) for p in args.frames]

    if args.still:
        frames[0].save(args.still)
        print(f"OK 静态帧 {args.still}")

    if args.pingpong and len(frames) > 2:
        frames = frames + frames[-2:0:-1]  # 1-2-3-4 -> +3-2

    # 自适应调色板，每帧量化到同一全局调色板，避免闪烁
    palette_src = frames[0].quantize(colors=256, method=Image.MEDIANCUT)
    palette = palette_src.getpalette()
    quantized = []
    for f in frames:
        q = f.quantize(colors=256, palette=palette_src, dither=Image.FLOYDSTEINBERG)
        quantized.append(q)

    duration = round(1000 / args.fps)

    if args.output.lower().endswith(".mp4"):
        import shutil
        import subprocess

        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            ffmpeg_exe = shutil.which("ffmpeg")
        if not ffmpeg_exe:
            raise SystemExit("缺少 ffmpeg：请 pip install imageio-ffmpeg 或安装系统 ffmpeg")

        # MP4 宽高需为偶数
        vw, vh = w - w % 2, h - h % 2
        clip = [f.crop((0, 0, vw, vh)) for f in frames]
        # 把往返序列重复到目标时长
        cycle_ms = len(clip) * duration
        loops = max(1, math.ceil(args.duration * 1000 / cycle_ms))
        clip = clip * loops

        proc = subprocess.Popen(
            [ffmpeg_exe, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{vw}x{vh}", "-r", str(args.fps), "-i", "-",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
             "-movflags", "+faststart", args.output],
            stdin=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        for frame in clip:
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise SystemExit("ffmpeg 编码失败")
        print(f"OK {args.output} (MP4, {len(clip)} 帧, 约 {len(clip) * duration / 1000:.1f}s)")
    else:
        quantized[0].save(
            args.output,
            save_all=True,
            append_images=quantized[1:],
            duration=duration,
            loop=0,
            optimize=True,
        )
        print(f"OK {args.output} ({len(quantized)} 帧, {duration}ms/帧)")


if __name__ == "__main__":
    main()
