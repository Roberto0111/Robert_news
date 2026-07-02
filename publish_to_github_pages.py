#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

try:
    from PIL import Image
except ModuleNotFoundError as exc:
    raise SystemExit("Missing dependency: Pillow. Install it with python3 -m pip install pillow") from exc


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout.strip()


def optional_run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def write_jpeg(source_path: Path, output_path: Path) -> None:
    with Image.open(source_path) as image:
        image = image.convert("RGB")
        image.save(output_path, format="JPEG", quality=93, optimize=True, progressive=False)


def ensure_repo(repo_dir: Path) -> None:
    if not (repo_dir / ".git").exists():
        raise RuntimeError(f"Git repo not found: {repo_dir}")
    if not optional_run(["git", "config", "--get", "user.name"], repo_dir):
        run(["git", "config", "user.name", "Roberto"], repo_dir)
    if not optional_run(["git", "config", "--get", "user.email"], repo_dir):
        run(["git", "config", "user.email", "roberto@example.local"], repo_dir)


def publish_assets(*, repo_dir: Path, report_date: str, dry_run: bool) -> list[str]:
    ensure_repo(repo_dir)
    day_dir = repo_dir / "daily" / report_date
    cards_dir = day_dir / "cards"
    if not cards_dir.exists():
        raise RuntimeError(f"Cards directory not found: {cards_dir}")

    card_paths = sorted(cards_dir.glob("final_*.png"))
    if len(card_paths) < 2:
        raise RuntimeError(f"Expected at least 2 final_*.png cards in {cards_dir}")

    ig_dir = repo_dir / "ig" / report_date
    ig_dir.mkdir(parents=True, exist_ok=True)
    image_urls: list[str] = []
    for index, card_path in enumerate(card_paths, start=1):
        suffix = card_path.stem.removeprefix("final_")
        out_name = f"{index:02d}_{suffix}.jpg"
        write_jpeg(card_path, ig_dir / out_name)
        image_urls.append(f"ig/{report_date}/{out_name}")

    latest_dir = repo_dir / "ig" / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    for old_path in latest_dir.glob("*.jpg"):
        old_path.unlink()
    for source_url in image_urls:
        source_path = repo_dir / source_url
        shutil.copy2(source_path, latest_dir / source_path.name)

    if dry_run:
        return image_urls

    run(["git", "add", "daily", "ig", "index.html"], repo_dir)
    staged = optional_run(["git", "diff", "--cached", "--name-only"], repo_dir)
    if staged:
        run(["git", "commit", "-m", f"Publish IG news assets {report_date}"], repo_dir)
        run(["git", "push", "-u", "origin", "main"], repo_dir)
    return image_urls


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish daily news image assets to GitHub Pages.")
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    pages_cfg: dict[str, Any] = config.get("github_pages", {})
    repo_dir = Path(str(pages_cfg.get("repo_dir") or args.repo)).expanduser().resolve()
    base_url = str(pages_cfg.get("base_url") or "https://roberto0111.github.io/Robert_news").rstrip("/")
    image_paths = publish_assets(repo_dir=repo_dir, report_date=args.date, dry_run=args.dry_run)
    for image_path in image_paths:
        print(f"{base_url}/{image_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
