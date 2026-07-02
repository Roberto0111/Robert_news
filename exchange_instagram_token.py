#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
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
        raise RuntimeError(f"Config not found: {path}")
    with path.open("rb") as f:
        return tomllib.load(f)


def get_value(section: dict[str, Any], key: str, env_key: str | None = None) -> str:
    if section.get(key):
        return str(section[key]).strip()
    if env_key and os.environ.get(env_key):
        return os.environ[env_key].strip()
    raise RuntimeError(f"Missing [{key}] in config or environment variable {env_key}.")


def replace_config_value(path: Path, section_name: str, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    in_section = False
    replaced = False
    section_seen = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_section and not replaced:
                output.append(f'{key} = "{value}"')
                replaced = True
            in_section = stripped == f"[{section_name}]"
            section_seen = section_seen or in_section
            output.append(line)
            continue
        if in_section and stripped.startswith(f"{key} "):
            output.append(f'{key} = "{value}"')
            replaced = True
        else:
            output.append(line)

    if not section_seen:
        output.append(f"[{section_name}]")
    if section_seen and in_section and not replaced:
        output.append(f'{key} = "{value}"')
    elif not section_seen:
        output.append(f'{key} = "{value}"')

    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Exchange or refresh an Instagram Login access token.")
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--config-section", default="instagram_news")
    parser.add_argument("--refresh", action="store_true", help="Refresh an existing long-lived token.")
    parser.add_argument("--write", action="store_true", help="Write the returned token back to config.toml.")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)
    section = config.get(args.config_section, {})
    access_token = get_value(section, "access_token", "IG_NEWS_ACCESS_TOKEN")

    if args.refresh:
        response = requests.get(
            "https://graph.instagram.com/refresh_access_token",
            params={"grant_type": "ig_refresh_token", "access_token": access_token},
            timeout=45,
        )
        stage = "refresh"
    else:
        app_secret = get_value(section, "app_secret", "IG_NEWS_APP_SECRET")
        response = requests.get(
            "https://graph.instagram.com/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": app_secret,
                "access_token": access_token,
            },
            timeout=45,
        )
        stage = "exchange"

    if not response.ok:
        raise RuntimeError(f"Instagram token {stage} failed ({response.status_code}): {response.text}")

    payload = response.json()
    new_token = str(payload.get("access_token") or "")
    expires_in = payload.get("expires_in")
    if not new_token:
        raise RuntimeError(f"Instagram token {stage} returned no access_token: {payload}")

    if args.write:
        replace_config_value(config_path, args.config_section, "access_token", new_token)
        print(f"Instagram token {stage} OK. Updated {config_path}.")
    else:
        print(f"Instagram token {stage} OK. Re-run with --write to update config.toml.")
    if expires_in:
        days = round(int(expires_in) / 86400, 1)
        print(f"Expires in about {days} days.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Instagram token exchange failed: {exc}")
        raise SystemExit(1)
