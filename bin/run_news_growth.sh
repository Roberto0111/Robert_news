#!/bin/zsh
set -euo pipefail

PROJECT_DIR="/Users/roberto/Automation/ig_daily_news_publisher"
PYTHON="/opt/anaconda3/bin/python3"
REPORT_DATE="${1:-$(TZ=Asia/Taipei date +%F)}"
LOG_FILE="${PROJECT_DIR}/logs/news_growth_launchd.log"

mkdir -p "${PROJECT_DIR}/logs"
cd "${PROJECT_DIR}"

{
  echo "[$(TZ=Asia/Taipei date '+%Y-%m-%d %H:%M:%S %Z')] News growth start date=${REPORT_DATE}"
  "${PYTHON}" growth/run_news_growth_pipeline.py --date "${REPORT_DATE}"
  echo "[$(TZ=Asia/Taipei date '+%Y-%m-%d %H:%M:%S %Z')] News growth completed"
} >> "${LOG_FILE}" 2>&1
