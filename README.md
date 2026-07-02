# IG Daily News Publisher

每日 20:00 產出「台灣迷因感」IG 直式新聞圖卡包。

## 固定風格

- 尺寸：1080 x 1350 px，IG 直式貼文 4:5
- 視覺：台灣迷因感、資訊框清楚、卡通主播、粗體繁中
- 內容：台灣熱門時事、國際新聞、科技新聞
- 原則：可以有梗，但不能亂講；每則新聞都要留來源

## 資料夾

```text
daily/
  YYYY-MM-DD/
    cards/
      final_01_cover.png
      final_02_*.png
      ...
    caption.md
    sources.md
    contact_sheet.png
templates/
  source_*.png
scripts/
  render_v2_bold_optimized.py
docs/
  github-deploy.md
```

## 每日產出規格

每天產出 6 張：

1. 封面
2. 台灣時事
3. 台灣生活或另一則台灣熱門
4. 國際新聞
5. 科技新聞
6. 今日總結

## 發 IG 建議

用 `publish_daily_to_ig.sh` 走 Meta/Instagram Graph API 自動發文：

```bash
cp config.example.toml config.toml
# 編輯 config.toml，填入 robertoo_news 對應的 ig_user_id，並設定 IG_NEWS_ACCESS_TOKEN
./publish_daily_to_ig.sh 2026-07-02
```

流程會先把 `daily/YYYY-MM-DD/cards/` 轉成公開 JPEG 並推到 GitHub Pages，再用公開 URL 建立 Instagram carousel。成功後會寫入 `daily/YYYY-MM-DD/ig_published.ok`，避免同一天重複發文。

注意：股市資金流向那組既有 token 目前對應 `@roberto__stock`，不能直接拿來發 `@robertoo_news`。
