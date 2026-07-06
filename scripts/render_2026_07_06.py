from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-06"
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

今天整理 2026/07/06 台灣時間可查核的重點：強颱巴威追平今年風王、10 和 11 日最接近台灣；中聯油案受害業者增至 360 家、18 項產品 30 批號公布；中國向太平洋試射可搭載核彈頭的潛射洲際彈道飛彈；科技版看到多語言研究，雙語者大腦年齡約年輕 6 歲。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #颱風巴威 #中聯油案 #食安 #中國飛彈 #人工智慧 #雙語 #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-06（台灣時間）

- 中央社，2026-07-06 17:58／18:22 更新，〈颱風巴威強度列今年風王 估10、11日距台最近〉
  https://www.cna.com.tw/news/ahel/202607060266.aspx
- 中央社，2026-07-06 17:15／19:26 更新，〈中聯油案受害業者增至360家 18項受影響產品、30批號公布〉
  https://www.cna.com.tw/news/ahel/202607060236.aspx
- 中央社，2026-07-06 14:45／17:47 更新，〈中國試射潛射洲際彈道飛彈 具備核打擊反擊能力〉
  https://www.cna.com.tw/news/acn/202607060160.aspx
- 中央社，2026-07-06 14:54，〈學外語延緩腦部老化 研究：雙語者大腦年輕6歲〉
  https://www.cna.com.tw/news/ait/202607060166.aspx
- 中央社聚焦頁，2026-07-06 查核；確認當日晚間熱門新聞排序與同日議題。
  https://www.cna.com.tw/list/headlines.aspx
- 中央社科技分類頁，2026-07-06 查核；確認當日科技分類最新稿件與熱門關鍵字。
  https://www.cna.com.tw/list/ait.aspx
"""
    manifest = {
        "date": "2026-07-06",
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
        ("cover", "2026.07.06", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "今天也是資訊量爆棚", ["今天 4 則重點一次看", "颱風、食安、飛彈、腦科學", "先看來源，再決定轉不轉"]),
        ("taiwan_typhoon_bavi", "台灣天氣", "巴威追平今年風王", "10、11 日距台最近，全台有雨", "風王不是封號，是警訊", ["中心風速每秒 60 公尺", "估 9 日白天發海警", "西半部、宜花防大雨豪雨"]),
        ("taiwan_food_oil", "台灣生活", "中聯油案增至 360 業者", "18 項產品、30 批號已公布", "先看批號，再看鍋子", ["問題油流向第 1、2 層下游", "符合條件午夜前預防下架", "食藥署專區每日更新進度"]),
        ("international_china_missile", "國際焦點", "中國試射潛射洲際飛彈", "太平洋公海落點，具核嚇阻意涵", "不是演習，是訊號", ["中午 12:01 自核潛艦發射", "中方稱事前通報相關國家", "外媒指測量船已部署太平洋"]),
        ("tech_bilingual_brain", "科技新梗", "學外語，大腦年輕 6 歲？", "研究：語言越多、越早學效果越好", "背單字突然有尊嚴", ["雙語者腦齡約年輕 6 歲", "4 種語言約年輕 13 歲", "研究仍提醒有其他影響因素"]),
        ("summary", "今日總結", "今天大概是這樣", "週一版：颱風、食安、區域安全、腦科學", "可以笑，但不要亂傳", ["台灣：巴威路徑＋油品批號", "國際：中國潛射飛彈試射", "科技：多語言與大腦老化"]),
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
