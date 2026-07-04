#!/bin/zsh
set -euo pipefail

PROJECT_DIR="/Users/roberto/Automation/ig_daily_news_publisher"
CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex"
REPORT_DATE="${1:-$(TZ=Asia/Taipei date +%F)}"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/daily_news_cron.log"
LOCK_DIR="${PROJECT_DIR}/.daily_news_${REPORT_DATE}.lock"
MARKER_PATH="${PROJECT_DIR}/daily/${REPORT_DATE}/ig_published.ok"

mkdir -p "${LOG_DIR}"

{
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] fallback check date=${REPORT_DATE}"

  if [[ -f "${MARKER_PATH}" ]]; then
    echo "already published: ${MARKER_PATH}"
    exit 0
  fi

  if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
    echo "another run is active: ${LOCK_DIR}"
    exit 0
  fi
  trap 'rmdir "${LOCK_DIR}" 2>/dev/null || true' EXIT

  cd "${PROJECT_DIR}"

  "${CODEX_BIN}" \
    --search \
    --ask-for-approval never \
    exec \
    --cd "${PROJECT_DIR}" \
    --sandbox danger-full-access \
    --model gpt-5.5 \
    "這是 robertoo_news 每日新聞圖卡 fallback 執行。REPORT_DATE=${REPORT_DATE}。

請完整執行每日新聞 IG 流程：
1. 在 ${PROJECT_DIR} 工作。
2. 若 daily/${REPORT_DATE}/ig_published.ok 已存在，停止並回報已發過。
3. 搜尋並查核 ${REPORT_DATE} 台灣時間當天的台灣熱門時事、國際新聞、科技新聞。資訊時間敏感，必須使用網路查證。
4. 使用既有 personalized_full_v2_bold_optimized 風格，產出 daily/${REPORT_DATE}/cards/final_01_cover.png 到 final_06_summary.png，共 6 張 1080x1350 圖卡；同時產出 caption.md、sources.md、manifest.json、contact_sheet.png。
5. 若圖卡生成失敗、新聞來源不足、或圖片文字明顯錯誤，停止，不要發 IG。
6. 發文前執行 /opt/anaconda3/bin/python3 post_to_instagram.py --config config.toml --caption-file daily/${REPORT_DATE}/caption.md --verify-account，若不是 @robertoo_news 立刻停止。
7. 可執行 /opt/anaconda3/bin/python3 exchange_instagram_token.py --config config.toml --refresh --write 刷新 token，但不要印出 access token、app_secret 或 config.toml 內容。
8. 執行 ./publish_daily_to_ig.sh ${REPORT_DATE} 發布 carousel。
9. 完成後確認 daily/${REPORT_DATE}/ig_published.ok 存在。

安全：不要要求 IG 密碼；不要把 config.toml 加入 git；不要印出任何 token 或 app_secret。"

  echo "fallback codex exec completed"
} >> "${LOG_FILE}" 2>&1
