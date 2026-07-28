#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "growth" / "output"
PUBLISHED = ROOT / "growth" / "published"
ANALYTICS = ROOT / "growth" / "analytics"
LOG = ROOT / "logs" / "news_growth.log"
LOCK = ROOT / ".news_growth.lock"
PYTHON = "/opt/anaconda3/bin/python3"
RAW_BASE = "https://raw.githubusercontent.com/Roberto0111/Robert_news/main/reels"


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{result.stdout}")
    return result


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"{dt.datetime.now().astimezone().isoformat(timespec='seconds')} {message}"
    with LOG.open("a", encoding="utf-8") as file:
        file.write(line + "\n")
    print(line)


def publish_video(source: Path, name: str) -> str:
    destination = ROOT / "reels" / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    relative = str(destination.relative_to(ROOT))
    run(["git", "add", relative])
    if run(["git", "diff", "--cached", "--quiet"], check=False).returncode != 0:
        run(["git", "commit", "-m", f"Add News growth Reel {name}"])
    run(["git", "push", "origin", "main"])
    url = f"{RAW_BASE}/{name}"
    local_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with urllib.request.urlopen(url, timeout=60) as response:
        remote_hash = hashlib.sha256(response.read()).hexdigest()
    if local_hash != remote_hash:
        raise RuntimeError(f"Published Reel hash mismatch: {url}")
    return url


def reel_caption(day_dir: Path) -> str:
    original = (day_dir / "caption.md").read_text(encoding="utf-8").strip()
    body = original.replace("# Caption", "").split("#Hashtags", 1)[0].strip()
    return f"""15 秒晚間新聞快報

{body}

完整背景與來源請看今天的輪播貼文。
先收藏，明早再看事件後續；也傳給今天沒空看新聞的人。

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #RobertoNews"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if LOCK.exists():
        raise RuntimeError(f"News growth lock exists: {LOCK}")
    LOCK.write_text(str(dt.datetime.now().timestamp()), encoding="utf-8")
    try:
        report_date = args.date or dt.datetime.now().astimezone().date().isoformat()
        day_dir = ROOT / "daily" / report_date
        if not (day_dir / "manifest.json").exists() or not (day_dir / "caption.md").exists():
            raise RuntimeError(f"News assets are incomplete: {day_dir}")
        marker = PUBLISHED / f"{report_date}_reel.json"
        if marker.exists() and not args.force:
            log(f"already published: {marker}")
            return 0

        OUTPUT.mkdir(parents=True, exist_ok=True)
        PUBLISHED.mkdir(parents=True, exist_ok=True)
        analyzer = run([PYTHON, "growth/analyze_instagram_performance.py"], check=False)
        if analyzer.returncode != 0:
            log(f"Insights unavailable; continuing with baseline strategy: {analyzer.stdout.strip()}")

        video = OUTPUT / f"{report_date}_news_reel.mp4"
        caption_file = OUTPUT / f"{report_date}_news_reel_caption.md"
        render_command = [
            PYTHON,
            "growth/render_news_reel_v2.py",
            "--day-dir",
            str(day_dir),
            "--output",
            str(video),
        ]
        run(render_command)
        caption_file.write_text(reel_caption(day_dir), encoding="utf-8")
        log(f"rendered News Reel: {video}")

        public_name = f"{report_date}-news-growth.mp4"
        if args.dry_run:
            result = run(
                [
                    PYTHON,
                    "post_to_instagram.py",
                    "--config",
                    "config.toml",
                    "--reel",
                    "--video-url",
                    f"{RAW_BASE}/{public_name}",
                    "--thumb-offset-ms",
                    "500",
                    "--caption-file",
                    str(caption_file),
                    "--dry-run",
                ]
            )
            log(f"dry-run complete: {result.stdout.splitlines()[0] if result.stdout else 'OK'}")
            return 0

        video_url = publish_video(video, public_name)
        result = run(
            [
                PYTHON,
                "post_to_instagram.py",
                "--config",
                "config.toml",
                "--reel",
                "--video-url",
                video_url,
                "--thumb-offset-ms",
                "500",
                "--caption-file",
                str(caption_file),
            ]
        )
        match = re.search(r"'id': '([^']+)'", result.stdout)
        payload = {
            "published_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "report_date": report_date,
            "instagram_media_id": match.group(1) if match else "",
            "video_url": video_url,
        }
        marker.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log(f"published News Reel media_id={payload['instagram_media_id'] or 'unknown'}")
        return 0
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
