#!/bin/zsh
set -euo pipefail

cd /Users/roberto/Automation/ig_daily_news_publisher

REPORT_DATE="${1:-$(date +%F)}"
FORCE="${2:-}"
DAILY_DIR="daily/${REPORT_DATE}"
MARKER_PATH="${DAILY_DIR}/ig_published.ok"

if [[ -f "${MARKER_PATH}" && "${FORCE}" != "--force" ]]; then
  echo "Already published for ${REPORT_DATE}: ${MARKER_PATH}"
  exit 0
fi

if [[ ! -d "${DAILY_DIR}/cards" ]]; then
  echo "Missing daily cards directory: ${DAILY_DIR}/cards" >&2
  exit 2
fi

if [[ ! -f "${DAILY_DIR}/caption.md" ]]; then
  echo "Missing caption: ${DAILY_DIR}/caption.md" >&2
  exit 3
fi

IMAGE_URLS=("${(@f)$(/opt/anaconda3/bin/python3 publish_to_github_pages.py --config config.toml --date "${REPORT_DATE}")}")

CACHE_BUSTER="$(date +%Y%m%d%H%M%S)"
POST_ARGS=()
for url in "${IMAGE_URLS[@]}"; do
  POST_ARGS+=(--image-url "${url}?v=${CACHE_BUSTER}")
done

/opt/anaconda3/bin/python3 post_to_instagram.py \
  --config config.toml \
  "${POST_ARGS[@]}" \
  --caption-file "${DAILY_DIR}/caption.md"

date '+%Y-%m-%d %H:%M:%S %Z' > "${MARKER_PATH}"
git add "${MARKER_PATH}"
git commit -m "Mark IG news published ${REPORT_DATE}" || true
git push -u origin main

echo "Published ${REPORT_DATE}; marker written: ${MARKER_PATH}"
