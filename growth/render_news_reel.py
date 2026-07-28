#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import struct
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1080
HEIGHT = 1920
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
BG = "#0b1015"
WHITE = "#f7f5ef"
MUTED = "#b8c0c8"
RED = "#ed3939"
CYAN = "#52d2d8"
GOLD = "#f2ba3d"
BASE_DURATIONS = (3, 3, 3, 3, 3)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def centered(draw: ImageDraw.ImageDraw, y: int, text: str, size: int, fill: str) -> None:
    fnt = font(size)
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text(((WIDTH - (box[2] - box[0])) / 2, y), text, font=fnt, fill=fill)


def fit_card(card_path: Path) -> Image.Image:
    with Image.open(card_path) as source:
        card = source.convert("RGB")
    card.thumbnail((940, 1175), Image.Resampling.LANCZOS)
    return card


def base_slide(date: str, section: str, index: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 118), fill="#050709")
    draw.rectangle((0, 118, 14, HEIGHT), fill=RED)
    draw.text((54, 32), "ROBERTO NEWS", font=font(32), fill=WHITE)
    draw.text((790, 37), date.replace("-", "."), font=font(24), fill=CYAN)
    draw.text((70, 164), section, font=font(26), fill=GOLD)
    draw.text((70, 1784), f"{index:02d} / 05", font=font(22), fill=MUTED)
    draw.rectangle((70, 1832, 1010, 1838), fill="#2c343b")
    draw.rectangle((70, 1832, 70 + 188 * index, 1838), fill=RED)
    return image, draw


def place_card(image: Image.Image, card_path: Path, y: int = 310) -> None:
    card = fit_card(card_path)
    x = (WIDTH - card.width) // 2
    shadow = Image.new("RGBA", (card.width + 18, card.height + 18), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle((8, 8, card.width + 8, card.height + 8), fill=(0, 0, 0, 105))
    image.paste(shadow, (x - 9, y - 9), shadow)
    image.paste(card, (x, y))


def section_for(path: Path) -> str:
    name = path.stem.lower()
    if "international" in name:
        return "國際快報"
    if "tech" in name:
        return "科技焦點"
    if "stock" in name or "finance" in name:
        return "財經焦點"
    return "台灣焦點"


def choose_cards(day_dir: Path) -> list[Path]:
    manifest_path = day_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    paths = [day_dir / item for item in manifest.get("cards", [])]
    paths = [path for path in paths if path.exists()]
    if len(paths) < 5:
        raise RuntimeError(f"Need at least five news cards in {manifest_path}.")
    return paths[1:5]


def render_slides(day_dir: Path, out_dir: Path, strategy: dict) -> list[Path]:
    date = day_dir.name
    cards = choose_cards(day_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slides: list[Path] = []

    for index, card_path in enumerate(cards, start=1):
        section = "今晚 15 秒新聞快報" if index == 1 else section_for(card_path)
        image, draw = base_slide(date, section, index)
        if index == 1:
            centered(draw, 228, "先看今天最重要的 4 件事", 44, WHITE)
        else:
            centered(draw, 228, "重點已整理在圖卡裡", 38, MUTED)
        place_card(image, card_path)
        centered(draw, 1600, "來源查核後整理｜完整內容見輪播貼文", 28, MUTED)
        path = out_dir / f"{index:02d}_news.png"
        image.save(path, "PNG", optimize=True)
        slides.append(path)

    image, draw = base_slide(date, "今晚新聞整理完畢", 5)
    centered(draw, 350, "15 秒看完", 52, MUTED)
    centered(draw, 500, "今天 4 件大事", 88, WHITE)
    draw.rectangle((150, 690, 930, 698), fill=RED)
    cta = strategy.get("format_settings", {}).get("cta", "save")
    if cta == "share":
        centered(draw, 875, "傳給今天沒空看新聞的人", 48, CYAN)
        centered(draw, 990, "你負責轉傳，我負責查來源", 38, WHITE)
    else:
        centered(draw, 875, "先收藏，明早再看事件後續", 48, CYAN)
        centered(draw, 990, "重要更新會整理在下一篇", 38, WHITE)
    centered(draw, 1325, "@robertoo_news", 42, GOLD)
    centered(draw, 1420, "追蹤｜收藏｜分享", 36, WHITE)
    centered(draw, 1600, "迷因感可以有，來源一定要留", 28, MUTED)
    path = out_dir / "05_cta.png"
    image.save(path, "PNG", optimize=True)
    slides.append(path)
    return slides


def write_soundtrack(path: Path, seconds: int) -> None:
    rate = 48_000
    total = rate * seconds
    audio = [0.0] * total
    beat = 60 / 100
    chords = (
        (110.00, 164.81, 220.00),
        (98.00, 146.83, 196.00),
        (130.81, 196.00, 261.63),
        (87.31, 130.81, 174.61),
        (110.00, 164.81, 220.00),
    )

    for position in range(total):
        elapsed = position / rate
        chord = chords[min(len(chords) - 1, int(elapsed / 3))]
        local = elapsed % 3
        envelope = min(1.0, local / 0.35, (3 - local) / 0.45)
        pad = sum(math.sin(2 * math.pi * frequency * elapsed) for frequency in chord)
        audio[position] += 0.018 * max(0.0, envelope) * pad

    for beat_index in range(math.ceil(seconds / beat)):
        start = beat_index * beat
        for index in range(int(0.22 * rate)):
            position = int(start * rate) + index
            if position >= total:
                break
            elapsed = index / rate
            frequency = 72.0 * ((48.0 / 72.0) ** min(1.0, elapsed / 0.18))
            audio[position] += 0.105 * math.sin(2 * math.pi * frequency * elapsed) * math.exp(-13 * elapsed)

        tick_start = int((start + beat / 2) * rate)
        for index in range(int(0.055 * rate)):
            position = tick_start + index
            if position >= total:
                break
            elapsed = index / rate
            tick = math.sin(2 * math.pi * 1550 * elapsed) + 0.45 * math.sin(2 * math.pi * 2350 * elapsed)
            audio[position] += 0.022 * tick * math.exp(-55 * elapsed)

    for transition in (0.0, 3.0, 6.0, 9.0, 12.0):
        start = int(transition * rate)
        for index in range(int(0.48 * rate)):
            position = start + index
            if position >= total:
                break
            elapsed = index / rate
            envelope = math.sin(math.pi * min(1.0, elapsed / 0.48)) * math.exp(-2.5 * elapsed)
            tone = math.sin(2 * math.pi * (330 + 220 * elapsed) * elapsed)
            audio[position] += 0.055 * envelope * tone

    fade_samples = int(0.25 * rate)
    peak = max(max(abs(value) for value in audio), 0.001)
    scale = 0.72 / peak
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        frames = bytearray()
        for index, sample in enumerate(audio):
            fade = min(1.0, index / fade_samples, (total - index - 1) / fade_samples)
            value = int(max(-1.0, min(1.0, sample * scale * max(0.0, fade))) * 32767)
            packed = struct.pack("<h", value)
            frames.extend(packed)
            frames.extend(packed)
        wav_file.writeframes(frames)


def render_video(slides: list[Path], output: Path, ffmpeg: str, durations: tuple[int, ...]) -> None:
    soundtrack = output.with_suffix(".wav")
    total_seconds = sum(durations)
    write_soundtrack(soundtrack, total_seconds)
    command = [ffmpeg, "-y"]
    for slide, duration in zip(slides, durations):
        command.extend(["-loop", "1", "-framerate", "30", "-t", str(duration), "-i", str(slide)])
    command.extend(["-i", str(soundtrack)])
    filters = []
    for index, duration in enumerate(durations):
        fade_in = "" if index == 0 else "fade=t=in:st=0:d=0.10,"
        filters.append(
            f"[{index}:v]scale={WIDTH}:{HEIGHT},"
            "zoompan=z='min(zoom+0.00035,1.018)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d=1:s={WIDTH}x{HEIGHT}:fps=30,"
            f"{fade_in}fade=t=out:st={duration - 0.10}:d=0.10,"
            f"setpts=PTS-STARTPTS[v{index}]"
        )
    streams = "".join(f"[v{index}]" for index in range(len(slides)))
    filters.append(f"{streams}concat=n={len(slides)}:v=1:a=0,format=yuv420p[v]")
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[v]",
            "-map",
            f"{len(slides)}:a",
            "-t",
            str(total_seconds),
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def durations_from_strategy(strategy: dict) -> tuple[int, ...]:
    settings = strategy.get("format_settings", {})
    hook = max(2, int(settings.get("hook_seconds", BASE_DURATIONS[0])))
    total = max(12, int(settings.get("total_seconds", sum(BASE_DURATIONS))))
    final = 3
    story_total = total - hook - final
    base, extra = divmod(story_total, 3)
    stories = [base + (1 if index < extra else 0) for index in range(3)]
    return (hook, *stories, final)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--strategy-json", default="")
    parser.add_argument("--ffmpeg", default="/opt/homebrew/bin/ffmpeg")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    strategy = {}
    if args.strategy_json and Path(args.strategy_json).exists():
        strategy = json.loads(Path(args.strategy_json).read_text(encoding="utf-8"))
    slides = render_slides(Path(args.day_dir), output.parent / f"{output.stem}_frames", strategy)
    render_video(slides, output, args.ffmpeg, durations_from_strategy(strategy))
    print(f"Rendered News Reel: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
