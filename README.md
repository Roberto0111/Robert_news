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

用 `daily/YYYY-MM-DD/cards/` 裡的 6 張圖建立 carousel 貼文。  
貼文文字使用同日期資料夾裡的 `caption.md`，發文前再快速檢查 `sources.md` 的來源連結。
