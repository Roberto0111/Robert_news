#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import struct
import subprocess
import wave
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


WIDTH = 1080
HEIGHT = 1920
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"
SAY = "/usr/bin/say"
BG = "#090d11"
WHITE = "#fbfaf7"
MUTED = "#bdc5cd"
RED = "#f23838"
CYAN = "#46d2d8"
GOLD = "#ffc342"
VOICE = "Reed (中文（台灣）)"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int = 34) -> ImageFont.FreeTypeFont:
    for size in range(start, minimum - 1, -2):
        candidate = font(size)
        if text_width(draw, text, candidate) <= max_width:
            return candidate
    return font(minimum)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if char in "，。！？；：、" and current and text_width(draw, candidate, fnt) > max_width:
            current = candidate
            continue
        if current and text_width(draw, candidate, fnt) > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def centered(draw: ImageDraw.ImageDraw, y: int, text: str, fnt: ImageFont.FreeTypeFont, fill: str) -> None:
    draw.text(((WIDTH - text_width(draw, text, fnt)) / 2, y), text, font=fnt, fill=fill)


def category_for(path: Path) -> str:
    name = path.stem.lower()
    if "international" in name:
        return "國際"
    if "tech" in name:
        return "科技"
    if "stock" in name or "finance" in name:
        return "財經"
    return "台灣"


def cards_from_manifest(day_dir: Path) -> list[Path]:
    manifest = json.loads((day_dir / "manifest.json").read_text(encoding="utf-8"))
    cards = [day_dir / item for item in manifest.get("cards", [])]
    cards = [path for path in cards if path.exists()]
    if len(cards) < 5:
        raise RuntimeError(f"Need at least five cards in {day_dir}.")
    return cards[1:5]


def fallback_script(day_dir: Path, cards: list[Path]) -> dict[str, Any]:
    caption = (day_dir / "caption.md").read_text(encoding="utf-8")
    body = caption.replace("# Caption", "").split("#Hashtags", 1)[0]
    paragraphs = [item.strip() for item in body.split("\n\n") if item.strip()]
    summary = max(paragraphs, key=len, default=body)
    if "：" in summary:
        summary = summary.split("：", 1)[1]
    candidates = [item.strip(" 。\n") for item in summary.split("；") if len(item.strip()) > 10][:4]
    scenes = []
    for index, card in enumerate(cards):
        narration = candidates[index] if index < len(candidates) else f"第 {index + 1} 則重點，完整內容請看圖卡。"
        if "台股" in narration:
            match = re.search(r"(\d+(?:\.\d+)?)\s*點", narration)
            accent = match.group(1) if match else "台股"
            title = f"台股重挫 {accent} 點" if match else "台股出現劇烈震盪"
            narration = f"台股受亞洲晶片股賣壓拖累，收盤重挫{accent}點。" if match else narration
        elif "特留分" in narration:
            title, accent = "遺產規則改了", "特留分"
            narration = "立法院三讀，刪除兄弟姊妹特留分，遺囑安排會變得更重要。"
        elif "熊本" in narration or "地震" in narration:
            match = re.search(r"規模\s*(\d+(?:\.\d+)?)", narration)
            accent = match.group(1) if match else "強震"
            title = f"熊本規模 {accent} 強震" if match else "日本發生強震"
            narration = f"日本熊本發生規模{accent}強震，災情和餘震仍要持續確認。"
        elif "蘋果" in narration and "輝達" in narration:
            title, accent = "蘋果超車輝達", "市值王"
            narration = "科技線是蘋果超車輝達，市場開始重新計算人工智慧的成本。"
        else:
            title, accent = narration[:16], category_for(card)
            narration = narration[:48].rstrip("，、；：") + "。"
        scenes.append(
            {
                "category": category_for(card),
                "title": title,
                "accent": accent,
                "narration": narration,
            }
        )
    return {
        "hook": scenes[0]["title"] + "，而且這還不是今天唯一的大事。",
        "scenes": scenes,
        "cta": "二十秒看完四件事。收藏這篇，明天一起追後續。",
    }


def load_script(day_dir: Path, script_path: Path | None) -> dict[str, Any]:
    cards = cards_from_manifest(day_dir)
    candidates = [script_path, day_dir / "reel_script.json"]
    for candidate in candidates:
        if candidate and candidate.exists():
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            if len(payload.get("scenes", [])) == 4:
                return payload
    return fallback_script(day_dir, cards)


def crop_background(card_path: Path) -> Image.Image:
    with Image.open(card_path) as source:
        card = source.convert("RGB")
    scale = max(WIDTH / card.width, 1430 / card.height)
    card = card.resize((round(card.width * scale), round(card.height * scale)), Image.Resampling.LANCZOS)
    x = max(0, (card.width - WIDTH) // 2)
    card = card.crop((x, 0, x + WIDTH, min(card.height, 1430)))
    card = ImageEnhance.Contrast(card).enhance(1.06)
    card = ImageEnhance.Color(card).enhance(1.08)
    return card


def render_scene(
    *,
    card_path: Path,
    scene: dict[str, str],
    date: str,
    index: int,
    output: Path,
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    background = crop_background(card_path)
    image.paste(background, (0, 285))

    top_scrim = Image.new("RGBA", (WIDTH, 400), (8, 12, 16, 238))
    image.paste(top_scrim, (0, 0), top_scrim)
    bottom_scrim = Image.new("RGBA", (WIDTH, 500), (8, 12, 16, 242))
    image.paste(bottom_scrim, (0, 1420), bottom_scrim)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH, 18), fill=RED)
    draw.text((54, 50), "ROBERTO NEWS", font=font(28), fill=WHITE)
    draw.text((812, 54), date.replace("-", "."), font=font(22), fill=CYAN)
    category = str(scene.get("category") or category_for(card_path))
    category_font = font(27)
    category_width = text_width(draw, category, category_font) + 42
    draw.rectangle((54, 118, 54 + category_width, 172), fill=RED)
    draw.text((75, 127), category, font=category_font, fill=WHITE)

    title = str(scene["title"])
    title_font = fit_font(draw, title, 940, 72, 46)
    centered(draw, 202, title, title_font, WHITE)

    accent = str(scene.get("accent") or "")
    if accent:
        accent_font = fit_font(draw, accent, 850, 116, 64)
        accent_width = text_width(draw, accent, accent_font)
        accent_x = (WIDTH - accent_width) / 2
        accent_y = 1472
        draw.rectangle((accent_x - 42, accent_y - 14, accent_x + accent_width + 42, accent_y + 132), fill=RED)
        draw.text((accent_x, accent_y), accent, font=accent_font, fill=WHITE)

    narration = str(scene["narration"])
    subtitle_font = font(34)
    lines = wrap_text(draw, narration, subtitle_font, 900)[:3]
    start_y = 1660
    for line_index, line in enumerate(lines):
        centered(draw, start_y + line_index * 52, line, subtitle_font, WHITE)

    draw.text((56, 1845), f"{index:02d} / 05", font=font(21), fill=MUTED)
    draw.rectangle((190, 1860, 1018, 1868), fill="#313941")
    draw.rectangle((190, 1860, 190 + round(828 * index / 5), 1868), fill=GOLD)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG", optimize=True)


def render_cta(date: str, cta: str, output: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    blurred = Image.new("RGB", (WIDTH, HEIGHT), "#101820").filter(ImageFilter.GaussianBlur(12))
    image.paste(blurred)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 18), fill=RED)
    draw.text((54, 50), "ROBERTO NEWS", font=font(28), fill=WHITE)
    draw.text((812, 54), date.replace("-", "."), font=font(22), fill=CYAN)
    centered(draw, 350, "今天不只一件大事", font(54), MUTED)
    centered(draw, 485, "20 秒看完", font(102), WHITE)
    draw.rectangle((150, 675, 930, 684), fill=RED)
    cta_lines = [item.strip() + "。" for item in cta.split("。") if item.strip()]
    if not cta_lines:
        cta_lines = wrap_text(draw, cta, font(38), 900)
    for index, line in enumerate(cta_lines[:3]):
        line_font = fit_font(draw, line, 900, 40, 32)
        centered(draw, 850 + index * 70, line, line_font, CYAN if index == 0 else WHITE)
    centered(draw, 1300, "@robertoo_news", font(46), GOLD)
    centered(draw, 1405, "追蹤｜收藏｜分享", font(36), WHITE)
    centered(draw, 1585, "迷因感可以有，來源一定要留", font(28), MUTED)
    draw.text((56, 1845), "05 / 05", font=font(21), fill=MUTED)
    draw.rectangle((190, 1860, 1018, 1868), fill=GOLD)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG", optimize=True)


def synthesize_voice(text: str, output: Path, voice: str, rate: int) -> float:
    subprocess.run([SAY, "-v", voice, "-r", str(rate), "-o", str(output), text], check=True)
    result = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(output)],
        check=True,
        text=True,
        capture_output=True,
    )
    return float(result.stdout.strip())


def write_soundtrack(path: Path, seconds: float) -> None:
    rate = 48_000
    total = round(rate * seconds)
    audio = [0.0] * total
    beat = 60 / 104
    chords = (
        (110.00, 164.81, 220.00),
        (98.00, 146.83, 196.00),
        (130.81, 196.00, 261.63),
        (87.31, 130.81, 174.61),
    )
    for position in range(total):
        elapsed = position / rate
        chord = chords[int(elapsed / 4) % len(chords)]
        pulse = 0.65 + 0.35 * math.sin(math.pi * (elapsed % beat) / beat)
        tone = sum(math.sin(2 * math.pi * frequency * elapsed) for frequency in chord)
        audio[position] += 0.015 * pulse * tone

    for beat_index in range(math.ceil(seconds / beat)):
        start = beat_index * beat
        for index in range(int(0.20 * rate)):
            position = int(start * rate) + index
            if position >= total:
                break
            elapsed = index / rate
            frequency = 70 * ((45 / 70) ** min(1.0, elapsed / 0.16))
            audio[position] += 0.10 * math.sin(2 * math.pi * frequency * elapsed) * math.exp(-14 * elapsed)
        tick_start = int((start + beat / 2) * rate)
        for index in range(int(0.045 * rate)):
            position = tick_start + index
            if position >= total:
                break
            elapsed = index / rate
            audio[position] += 0.018 * math.sin(2 * math.pi * 1850 * elapsed) * math.exp(-65 * elapsed)

    for start_seconds in (0.0, 4.0, 8.0, 12.0, 16.0):
        for index in range(int(0.42 * rate)):
            position = int(start_seconds * rate) + index
            if position >= total:
                break
            progress = index / (0.42 * rate)
            envelope = math.sin(math.pi * progress)
            audio[position] += 0.04 * envelope * math.sin(2 * math.pi * (320 + 180 * progress) * index / rate)

    fade_samples = int(0.25 * rate)
    peak = max(max(abs(value) for value in audio), 0.001)
    scale = 0.62 / peak
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


def render_video(
    frames: list[Path],
    voice_paths: list[Path],
    durations: list[float],
    soundtrack: Path,
    output: Path,
) -> None:
    command = [FFMPEG, "-y"]
    for frame, duration in zip(frames, durations):
        command.extend(["-loop", "1", "-framerate", "30", "-t", f"{duration:.3f}", "-i", str(frame)])
    for voice in voice_paths:
        command.extend(["-i", str(voice)])
    command.extend(["-i", str(soundtrack)])

    filters: list[str] = []
    for index, duration in enumerate(durations):
        if index % 2:
            zoom = "min(zoom+0.00075,1.055)"
            x = "iw/2-(iw/zoom/2)+8*sin(on/18)"
        else:
            zoom = "if(eq(on,0),1.055,max(1.0,zoom-0.00065))"
            x = "iw/2-(iw/zoom/2)-8*sin(on/18)"
        fade_in = "" if index == 0 else "fade=t=in:st=0:d=0.10,"
        filters.append(
            f"[{index}:v]scale={WIDTH}:{HEIGHT},"
            f"zoompan=z='{zoom}':x='{x}':y='ih/2-(ih/zoom/2)':"
            f"d=1:s={WIDTH}x{HEIGHT}:fps=30,"
            f"{fade_in}fade=t=out:st={max(0.0, duration - 0.10):.3f}:d=0.10,"
            f"setpts=PTS-STARTPTS[v{index}]"
        )
    video_streams = "".join(f"[v{index}]" for index in range(len(frames)))
    filters.append(f"{video_streams}concat=n={len(frames)}:v=1:a=0,format=yuv420p[video]")

    voice_offset = len(frames)
    for index, duration in enumerate(durations):
        filters.append(
            f"[{voice_offset + index}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"apad=pad_dur=1,atrim=duration={duration:.3f},asetpts=PTS-STARTPTS[a{index}]"
        )
    voice_streams = "".join(f"[a{index}]" for index in range(len(voice_paths)))
    filters.append(f"{voice_streams}concat=n={len(voice_paths)}:v=0:a=1[voice]")
    music_index = len(frames) + len(voice_paths)
    filters.append(f"[{music_index}:a]volume=0.20[music]")
    filters.append(
        "[voice][music]amix=inputs=2:duration=first:weights='1 0.34':normalize=0,"
        "loudnorm=I=-16:LRA=7:TP=-1.5[audio]"
    )

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[video]",
            "-map",
            "[audio]",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            "+faststart",
            "-shortest",
            str(output),
        ]
    )
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--script-json", default="")
    parser.add_argument("--voice", default=VOICE)
    parser.add_argument("--voice-rate", type=int, default=225)
    args = parser.parse_args()

    day_dir = Path(args.day_dir)
    output = Path(args.output)
    work = output.parent / f"{output.stem}_v2_assets"
    work.mkdir(parents=True, exist_ok=True)
    cards = cards_from_manifest(day_dir)
    script = load_script(day_dir, Path(args.script_json) if args.script_json else None)

    scenes = list(script["scenes"])
    scenes[0] = {**scenes[0], "narration": str(script.get("hook") or scenes[0]["narration"])}
    frames: list[Path] = []
    voice_paths: list[Path] = []
    durations: list[float] = []
    for index, (card, scene) in enumerate(zip(cards, scenes), start=1):
        frame = work / f"{index:02d}_scene.png"
        voice = work / f"{index:02d}_voice.aiff"
        render_scene(card_path=card, scene=scene, date=day_dir.name, index=index, output=frame)
        voice_seconds = synthesize_voice(str(scene["narration"]), voice, args.voice, args.voice_rate)
        frames.append(frame)
        voice_paths.append(voice)
        durations.append(max(3.0, voice_seconds + 0.35))

    cta_text = str(script.get("cta") or "收藏這篇，明天一起追後續。")
    cta_frame = work / "05_cta.png"
    cta_voice = work / "05_voice.aiff"
    render_cta(day_dir.name, cta_text, cta_frame)
    cta_seconds = synthesize_voice(cta_text, cta_voice, args.voice, args.voice_rate)
    frames.append(cta_frame)
    voice_paths.append(cta_voice)
    durations.append(max(3.0, cta_seconds + 0.35))

    soundtrack = work / "newsroom_bgm.wav"
    write_soundtrack(soundtrack, sum(durations))
    output.parent.mkdir(parents=True, exist_ok=True)
    render_video(frames, voice_paths, durations, soundtrack, output)
    print(f"Rendered animated narrated News Reel: {output}")
    print(f"Duration: {sum(durations):.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
