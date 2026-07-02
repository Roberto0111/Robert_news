#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

try:
    import requests
except ModuleNotFoundError as exc:
    raise SystemExit("Missing dependency: requests. Install it with python3 -m pip install requests") from exc


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def get_token(ig_cfg: dict[str, Any], cli_token: str | None) -> str:
    if cli_token:
        return cli_token.strip()
    if ig_cfg.get("access_token"):
        return str(ig_cfg["access_token"]).strip()
    env_name = str(ig_cfg.get("access_token_env") or "IG_NEWS_ACCESS_TOKEN")
    token = os.environ.get(env_name)
    if token:
        return token.strip()
    raise RuntimeError(
        f"Instagram access token not found. Set environment variable {env_name} "
        f"or put access_token in the private local config.toml."
    )


def raise_for_meta_error(response: requests.Response, stage: str) -> None:
    if response.ok:
        return
    detail = response.text
    try:
        payload = response.json()
        error = payload.get("error", {})
        safe_error = {
            key: error.get(key)
            for key in [
                "message",
                "type",
                "code",
                "error_subcode",
                "error_user_title",
                "error_user_msg",
                "fbtrace_id",
            ]
            if error.get(key) is not None
        }
        if safe_error:
            detail = json.dumps(safe_error, ensure_ascii=False)
    except ValueError:
        pass
    raise RuntimeError(f"Meta API {stage} failed ({response.status_code}): {detail}")


def get_account_username(*, ig_user_id: str, access_token: str, api_version: str) -> str:
    if access_token.startswith("IG"):
        res = requests.get(
            f"https://graph.instagram.com/{api_version}/me",
            params={"fields": "user_id,username", "access_token": access_token},
            timeout=45,
        )
        raise_for_meta_error(res, "account verify")
        payload = res.json()
        if isinstance(payload.get("data"), list) and payload["data"]:
            payload = payload["data"][0]
        user_id = str(payload.get("user_id") or "")
        if user_id and user_id != ig_user_id:
            raise RuntimeError(f"Configured IG user id is {ig_user_id}, but token is for {user_id}.")
        return str(payload.get("username") or "")

    res = requests.get(
        f"https://graph.facebook.com/{api_version}/{ig_user_id}",
        params={"fields": "username", "access_token": access_token},
        timeout=45,
    )
    raise_for_meta_error(res, "account verify")
    return str(res.json().get("username") or "")


def post_carousel(
    *,
    ig_user_id: str,
    access_token: str,
    image_urls: list[str],
    caption: str,
    api_version: str,
    publish_delay_seconds: int,
    dry_run: bool,
) -> dict[str, Any]:
    if len(image_urls) < 2:
        raise RuntimeError("Carousel publishing needs at least 2 image URLs.")
    if len(image_urls) > 10:
        raise RuntimeError("Instagram carousel supports at most 10 items.")

    graph_host = "graph.instagram.com" if access_token.startswith("IG") else "graph.facebook.com"
    create_url = f"https://{graph_host}/{api_version}/{ig_user_id}/media"
    publish_url = f"https://{graph_host}/{api_version}/{ig_user_id}/media_publish"

    if dry_run:
        return {
            "dry_run": True,
            "create_url": create_url,
            "publish_url": publish_url,
            "image_urls": image_urls,
            "caption": caption,
        }

    child_ids: list[str] = []
    for image_url in image_urls:
        child_res = requests.post(
            create_url,
            data={
                "image_url": image_url,
                "media_type": "IMAGE",
                "is_carousel_item": "true",
                "access_token": access_token,
            },
            timeout=45,
        )
        raise_for_meta_error(child_res, "carousel child create")
        child_ids.append(str(child_res.json()["id"]))

    create_res = requests.post(
        create_url,
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
            "access_token": access_token,
        },
        timeout=45,
    )
    raise_for_meta_error(create_res, "carousel create")
    creation_id = str(create_res.json()["id"])

    if publish_delay_seconds > 0:
        time.sleep(publish_delay_seconds)

    publish_res = requests.post(
        publish_url,
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=45,
    )
    raise_for_meta_error(publish_res, "media publish")
    return {"creation_id": creation_id, "publish": publish_res.json()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a daily news carousel to Instagram.")
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--config-section", default="instagram_news")
    parser.add_argument("--ig-user-id")
    parser.add_argument("--access-token")
    parser.add_argument("--api-version")
    parser.add_argument("--expected-username")
    parser.add_argument("--image-url", action="append", default=[])
    parser.add_argument("--caption-file", required=True)
    parser.add_argument("--publish-delay-seconds", type=int)
    parser.add_argument("--verify-account", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    ig_cfg = config.get(args.config_section, {})
    if ig_cfg.get("enabled") is False and not args.dry_run:
        print(f"Instagram posting skipped: [{args.config_section}].enabled is false.")
        return 0

    ig_user_id = str(args.ig_user_id or ig_cfg.get("ig_user_id") or "").strip()
    if not ig_user_id:
        raise RuntimeError(f"Instagram ig_user_id is missing in [{args.config_section}].")
    api_version = str(args.api_version or ig_cfg.get("api_version") or "v21.0").strip()
    access_token = get_token(ig_cfg, args.access_token)
    expected_username = str(args.expected_username or ig_cfg.get("expected_username") or "").strip().lstrip("@")

    username = get_account_username(ig_user_id=ig_user_id, access_token=access_token, api_version=api_version)
    if expected_username and username != expected_username:
        raise RuntimeError(f"Configured IG user is @{username}, expected @{expected_username}.")
    if args.verify_account:
        print(f"Instagram account verified: @{username}")
        return 0

    image_urls = [str(item).strip() for item in args.image_url if str(item).strip()]
    caption = Path(args.caption_file).read_text(encoding="utf-8").strip()
    publish_delay_seconds = int(
        args.publish_delay_seconds
        if args.publish_delay_seconds is not None
        else ig_cfg.get("publish_delay_seconds", 8)
    )

    result = post_carousel(
        ig_user_id=ig_user_id,
        access_token=access_token,
        image_urls=image_urls,
        caption=caption,
        api_version=api_version,
        publish_delay_seconds=publish_delay_seconds,
        dry_run=args.dry_run,
    )
    if args.dry_run:
        print(f"Instagram dry run OK for @{username}.")
        print("Carousel image URLs:")
        for image_url in result["image_urls"]:
            print(image_url)
        print("Caption:")
        print(result["caption"])
    else:
        print(f"Instagram posted to @{username}: {result['publish']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Instagram publish failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
