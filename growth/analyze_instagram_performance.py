#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import requests

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore


def graph_base(token: str, version: str) -> str:
    host = "graph.instagram.com" if token.startswith("IG") else "graph.facebook.com"
    return f"https://{host}/{version}"


def get(base: str, path: str, token: str, **params: Any) -> requests.Response:
    return requests.get(
        f"{base}/{path.lstrip('/')}",
        params={**params, "access_token": token},
        timeout=45,
    )


def metric_value(entry: dict[str, Any]) -> float:
    if "total_value" in entry:
        value = entry["total_value"].get("value", 0)
    else:
        value = (entry.get("values") or [{}])[0].get("value", 0)
    return float(value or 0)


def summarize(posts: list[dict[str, Any]]) -> dict[str, float | int]:
    samples = len(posts)
    totals = {
        name: sum(float(post["metrics"].get(name, 0)) for post in posts)
        for name in ("views", "reach", "shares", "saved", "total_interactions")
    }
    watch = [
        float(post["metrics"]["ig_reels_avg_watch_time"])
        for post in posts
        if post["metrics"].get("ig_reels_avg_watch_time")
    ]
    return {
        "samples": samples,
        "avg_views": totals["views"] / samples if samples else 0,
        "avg_reach": totals["reach"] / samples if samples else 0,
        "interaction_rate": totals["total_interactions"] / totals["reach"] if totals["reach"] else 0,
        "share_rate": totals["shares"] / totals["reach"] if totals["reach"] else 0,
        "save_rate": totals["saved"] / totals["reach"] if totals["reach"] else 0,
        "avg_watch_time_ms": sum(watch) / len(watch) if watch else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--output-dir", default="growth/analytics")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    latest_path = output_dir / "latest.json"
    today = dt.datetime.now().astimezone().date().isoformat()
    if latest_path.exists() and not args.force:
        cached = json.loads(latest_path.read_text(encoding="utf-8"))
        if str(cached.get("collected_at", "")).startswith(today):
            print("News strategy cache is current; skipping duplicate Insights requests.")
            return 0

    with Path(args.config).open("rb") as file:
        cfg = tomllib.load(file)["instagram_news"]
    token = str(cfg["access_token"])
    user_id = str(cfg["ig_user_id"])
    base = graph_base(token, str(cfg.get("api_version", "v20.0")))

    profile_response = get(
        base,
        user_id if not token.startswith("IG") else "me",
        token,
        fields="id,user_id,username,followers_count,follows_count,media_count",
    )
    if not profile_response.ok:
        raise RuntimeError(f"Instagram profile request failed: HTTP {profile_response.status_code}")
    profile = profile_response.json()
    if isinstance(profile.get("data"), list) and profile["data"]:
        profile = profile["data"][0]

    media_response = get(
        base,
        f"{user_id}/media",
        token,
        fields="id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count",
        limit=20,
    )
    if not media_response.ok:
        raise RuntimeError(f"Instagram media request failed: HTTP {media_response.status_code}")

    media = media_response.json().get("data", [])
    reels = [item for item in media if item.get("media_product_type") == "REELS"][:8]
    feed = [item for item in media if item.get("media_product_type") != "REELS"][:8]
    selected_ids = {str(item.get("id")) for item in reels + feed}
    selected_media = [item for item in media if str(item.get("id")) in selected_ids]

    posts = []
    insight_successes = 0
    permission_error = ""
    for item in selected_media:
        metrics: dict[str, float] = {}
        response = get(
            base,
            f"{item['id']}/insights",
            token,
            metric="views,reach,saved,shares,total_interactions",
        )
        if response.ok:
            insight_successes += 1
            metrics.update({entry["name"]: metric_value(entry) for entry in response.json().get("data", [])})
            if item.get("media_product_type") == "REELS":
                watch = get(
                    base,
                    f"{item['id']}/insights",
                    token,
                    metric="ig_reels_avg_watch_time,ig_reels_video_view_total_time",
                )
                if watch.ok:
                    metrics.update({entry["name"]: metric_value(entry) for entry in watch.json().get("data", [])})
        elif not permission_error:
            try:
                permission_error = str(response.json().get("error", {}).get("message") or "Insights unavailable")
            except ValueError:
                permission_error = f"HTTP {response.status_code}"
        posts.append({**item, "metrics": metrics})

    insights_available = insight_successes > 0
    reels = [post for post in posts if post.get("media_product_type") == "REELS"]
    feed = [post for post in posts if post.get("media_product_type") != "REELS"]
    reel_stats = summarize(reels)
    feed_stats = summarize(feed)
    settings = {"hook_seconds": 3, "total_seconds": 15, "cta": "save"}
    recommendations = []
    if not insights_available:
        recommendations.append("目前無法讀取 Insights；維持 15 秒新聞快報，不依單篇讚數改版。")
    elif reel_stats["samples"] < 3:
        recommendations.append("新聞 Reel 少於 3 支，先固定格式累積樣本。")
    else:
        if 0 < reel_stats["avg_watch_time_ms"] < 5500:
            settings["hook_seconds"] = 2
            settings["total_seconds"] = 12
            recommendations.append("平均觀看低於 5.5 秒；下一支把開場縮到 2 秒、總長縮到 12 秒。")
        if reel_stats["share_rate"] < 0.005:
            settings["cta"] = "share"
            recommendations.append("分享率偏低；下一支結尾改成轉傳型 CTA，頭條優先採高公共影響事件。")
        if reel_stats["save_rate"] < 0.01 and settings["cta"] != "share":
            recommendations.append("收藏率偏低；結尾提醒收藏並追蹤隔日後續。")
        if reel_stats["avg_reach"] > feed_stats["avg_reach"]:
            recommendations.append("Reel 平均觸及較高；保留快報，輪播繼續提供完整背景。")
        else:
            recommendations.append("輪播觸及不低於 Reel；Reel 下一支提早顯示頭條與數字。")

    now = dt.datetime.now().astimezone()
    payload = {
        "collected_at": now.isoformat(timespec="seconds"),
        "profile": profile,
        "insights_available": insights_available,
        "permission_error": "" if insights_available else permission_error,
        "reels": reel_stats,
        "feed": feed_stats,
        "format_settings": settings,
        "recommendations": recommendations,
        "posts": posts,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    (output_dir / f"{stamp}.json").write_text(serialized, encoding="utf-8")
    (output_dir / "latest.json").write_text(serialized, encoding="utf-8")
    strategy = [
        "# News Daily Growth Strategy",
        "",
        f"Updated: {now.isoformat(timespec='seconds')}",
        f"Account: @{profile.get('username')}",
        f"Followers: {profile.get('followers_count')}",
        f"Insights available: {'yes' if insights_available else 'no'}",
        "",
        "## Next Post",
        "",
        *[f"- {item}" for item in recommendations],
        "",
        "## Guardrails",
        "",
        "- 新聞事實只使用當日已查核的來源與存檔圖卡。",
        "- 至少累積 3 支 Reel 才調整節奏。",
        "- Reel 負責觸及，輪播負責完整脈絡，兩者都保留。",
    ]
    (output_dir / "daily_strategy.md").write_text("\n".join(strategy) + "\n", encoding="utf-8")
    print(
        f"News strategy updated: followers={profile.get('followers_count')} "
        f"insights={'yes' if insights_available else 'no'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
