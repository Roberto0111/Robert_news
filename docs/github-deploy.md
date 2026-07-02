# GitHub 部署筆記

這個資料夾可以直接當作 GitHub repo 根目錄。

## 建 repo

```bash
cd /Users/roberto/Documents/Codex/2026-07-02/new-chat-2/outputs/ig_daily_news_publisher
git init
git add .
git commit -m "Initial IG daily news publisher"
git branch -M main
git remote add origin <你的 GitHub repo URL>
git push -u origin main
```

## GitHub Pages

如果只是要保存每天產出的圖片和 caption，普通 GitHub repo 就夠了。

如果想要有網頁預覽，可以開 GitHub Pages：

1. 到 repo 的 Settings
2. Pages
3. Source 選 Deploy from a branch
4. Branch 選 `main`
5. Folder 選 `/root`

之後可以再加一個 `index.html` 做每日素材瀏覽頁。

## IG 發文

GitHub 可以保存素材，但不等於會自動發 IG。自動發 IG 通常需要：

- Instagram Business 或 Creator 帳號
- Meta app
- Facebook Page 綁定
- Instagram Graph API 權限

比較穩的流程是：每天先自動產出圖卡和 caption，人工檢查後再發文。
