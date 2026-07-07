from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-07"
OUT = DAILY / "cards"

FONT = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc"
FALLBACK = "/System/Library/Fonts/STHeiti Medium.ttc"


def font(size):
    for path in (FONT, FALLBACK):
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def tw(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def fit(draw, text, max_width, size, min_size=24):
    while size >= min_size:
        f = font(size)
        if tw(draw, text, f) <= max_width:
            return f
        size -= 2
    return font(min_size)


def wrap(draw, text, fnt, max_width):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if tw(draw, test, fnt) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def rr(draw, xy, radius, fill, outline=(31, 35, 38, 255), width=4):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def bold(draw, xy, text, fnt, fill=(30, 35, 38, 255), anchor=None, stroke=1):
    draw.text(
        xy,
        text,
        font=fnt,
        fill=fill,
        anchor=anchor,
        stroke_width=stroke,
        stroke_fill=(30, 35, 38, 255) if stroke > 1 else (255, 250, 232, 210),
    )


def fit_cover(path):
    im = Image.open(path).convert("RGB")
    return ImageOps.fit(im, (1080, 1350), method=Image.LANCZOS, centering=(0.5, 0.48)).convert("RGBA")


def overlay(src_path, spec, idx):
    im = fit_cover(src_path)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    rr(d, (48, 42, 1032, 222), 34, (255, 255, 255, 222), width=5)
    tag_f = font(32)
    title_f = fit(d, spec["title"], 845, spec.get("title_size", 59), 34)
    sub_f = fit(d, spec["subtitle"], 810, 30, 22)

    rr(d, (78, 70, 78 + tw(d, spec["tag"], tag_f) + 38, 120), 23, (255, 213, 70, 250), width=4)
    bold(d, (97, 76), spec["tag"], tag_f, fill=(224, 63, 47, 255), stroke=0)
    bold(d, (82, 124), spec["title"], title_f, stroke=1)
    bold(d, (84, 182), spec["subtitle"], sub_f, fill=(20, 128, 132, 255), stroke=0)

    rr(d, (84, 1130, 996, 1304), 30, (255, 255, 255, 226), width=5)
    bullet_f = font(33)
    y = 1151
    for bullet in spec["bullets"]:
        d.ellipse((112, y + 8, 136, y + 32), fill=(255, 213, 70, 255), outline=(31, 35, 38, 255), width=3)
        lines = wrap(d, bullet, bullet_f, 785)
        bold(d, (154, y - 1), lines[0], bullet_f, stroke=1)
        y += 44

    punch_f = fit(d, spec["punch"], 540, 36, 25)
    rr(d, (274, 1044, 806, 1100), 28, (255, 213, 70, 238), width=4)
    bold(d, (540, 1055), spec["punch"], punch_f, anchor="ma", stroke=0)

    final = Image.alpha_composite(im, ov).convert("RGB")
    out = OUT / f"final_{idx:02d}_{spec['slug']}.png"
    final.save(out, quality=95)
    return out


def write_text_files(cards):
    caption = """# Caption

今晚新聞梗圖包來了。

今天整理 2026/07/07 台灣時間可查核的重點：強颱巴威最新侵襲機率出爐，9 縣市飆破 9 成；中聯油品案公布 232 項產品明細、已回收逾 43 噸；中國試射潛射洲際彈道飛彈，國際反彈聲浪持續；AI 晶片股回檔拖累亞股，台股重挫 1077 點。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #颱風巴威 #中聯油品 #食安 #中國飛彈 #AI晶片 #台股 #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-07（台灣時間）

- 中央社首頁／聚焦與影音，2026-07-07 查核；確認當日晚間熱門排序包含巴威侵襲機率、中聯油品、台股與國際新聞。
  https://www.cna.com.tw/
- 中央社，2026-07-07 16:54／17:39 更新，〈食藥署公布致癌油232項產品明細 已回收逾43噸〉
  https://www.cna.com.tw/news/ahel/202607070257.aspx
- 中央社，2026-07-07，〈中國試射潛射洲際彈道飛彈 國際最新反彈聲浪一覽〉
  https://www.cna.com.tw/news/aopl/202607070314.aspx
- 中央社，2026-07-07，〈台股重挫1077點史上第8大跌點 高價電子股慘綠〉
  https://www.cna.com.tw/news/afe/202607070184.aspx
- 中央社科技分類頁，2026-07-07 查核；確認當日科技與 AI 相關新聞排序。
  https://www.cna.com.tw/list/ait.aspx
- 公視新聞網，2026-07-06 發布／2026-07-07 09:33 更新，〈颱風巴威穩定向西行進 氣象署估7/9北轉接近台灣〉
  https://news.pts.org.tw/article/816278
- 鉅亨網／優分析，2026-07-07 18:00，〈新興市場股市紛紛重挫 AI晶片股回檔拖累南韓、台灣市場〉
  https://news.cnyes.com/news/id/6525836
"""
    manifest = {
        "date": "2026-07-07",
        "style": "personalized_full_v2_bold_optimized",
        "size": "1080x1350",
        "cards": [f"cards/{card.name}" for card in cards],
        "caption": "caption.md",
        "sources": "sources.md",
    }
    (DAILY / "caption.md").write_text(caption, encoding="utf-8")
    (DAILY / "sources.md").write_text(sources, encoding="utf-8")
    (DAILY / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = [
        SRC / "source_cover.png",
        SRC / "source_island_policy.png",
        SRC / "source_food_safety.png",
        SRC / "source_us_jobs.png",
        SRC / "source_tech_gaming.png",
        SRC / "source_summary.png",
    ]
    for p in sources:
        shutil.copy2(p, DAILY / p.name)

    specs = [
        ("cover", "2026.07.07", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "先看來源，再決定轉發", ["今天 4 則重點一次看", "颱風、食安、飛彈、AI股", "可以有梗，但不能亂講"]),
        ("taiwan_typhoon_bavi", "台灣天氣", "巴威侵襲率 9 縣市破 9 成", "暴風半徑 350 公里，9 日恐發警報", "先收陽台，再問放假", ["估 9 日海陸警齊發", "10 日傍晚暴風圈觸陸", "週五六影響最劇烈"]),
        ("taiwan_food_oil", "台灣生活", "致癌油 232 項明細公布", "中聯油案已回收逾 43 噸", "先看名單，再看鍋子", ["受害業者仍以 360 家估算", "331 家已掌握、29 家追蹤中", "第 2 層下游即起全面下架"]),
        ("international_china_missile", "國際焦點", "中國試射潛射洲際飛彈", "澳洲、索羅門與北約陸續反彈", "不是煙火，是訊號", ["太平洋公海落點引關切", "澳洲稱區域安全受威脅", "北約示警別對北京天真"]),
        ("tech_ai_stocks", "科技財經", "AI 晶片股回檔拖累亞股", "台股重挫 1077 點，韓股又熔斷", "財報亮，股價照樣抖", ["市場重估 AI 高估值", "KOSPI 盤中觸發熔斷", "台股跌點史上第 8 大"]),
        ("summary", "今日總結", "今天大概是這樣", "週二版：颱風、食安、區域安全、AI 股", "可以笑，但不要亂傳", ["台灣：巴威＋油品名單", "國際：中國飛彈反彈升溫", "科技：AI 股回檔衝擊亞股"]),
    ]
    specs = [
        {"slug": s, "tag": t, "title": title, "subtitle": sub, "punch": p, "bullets": b}
        for s, t, title, sub, p, b in specs
    ]
    outs = [overlay(src, spec, i) for i, (src, spec) in enumerate(zip(sources, specs), 1)]

    thumbs = [Image.open(p).resize((180, 225), Image.LANCZOS) for p in outs]
    sheet = Image.new("RGB", (180 * len(thumbs), 225), (245, 245, 240))
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, (180 * i, 0))
    sheet.save(DAILY / "contact_sheet.png", quality=95)
    write_text_files(outs)

    for p in outs:
        print(p, Image.open(p).size)
    print(DAILY / "contact_sheet.png")


if __name__ == "__main__":
    main()
