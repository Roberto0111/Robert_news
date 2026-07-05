from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-05"
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

今天整理 2026/07/05 台灣時間可查核的重點：颱風巴威可能 10、11 日最接近台灣，中聯油品案擴大公布受影響業者與下架時程，美國國慶夜紐約布魯克林發生槍擊，以及 X Money 把社群平台往金融服務推進。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #颱風巴威 #食安 #美國新聞 #XMoney #FinTech #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-05（台灣時間）

- 中央社，2026-07-05 17:51／18:08 更新，〈颱風巴威10、11日距台最近 侵襲新竹以北、宜花機率逾4成〉
  https://www.cna.com.tw/news/ahel/202607050156.aspx
- 中央社，2026-07-05 18:18／18:48 更新，〈食藥署公布257家中聯問題油品受害業者 鼓勵小吃店主動揭露〉
  https://www.cna.com.tw/news/ahel/202607050163.aspx
- 中央社，2026-07-05 17:32／17:53 更新，〈美國國慶夜紐約布魯克林爆槍擊 至少8人中槍〉
  https://www.cna.com.tw/news/aopl/202607050153.aspx
- 中央社，2026-07-05 16:29，〈馬斯克推動X轉型超級App 旗下X Money擬進軍日本〉；作為 2026-07-05 科技平台與金融科技新聞主卡來源。
  https://www.cna.com.tw/news/aopl/202607050127.aspx
- 中央社，2026-07-05 19:03，〈專家示警太平洋恐掀戰 籲澳洲思考中國若侵台如何應戰〉；用於國際台海安全背景備查，未作主卡。
  https://www.cna.com.tw/news/aopl/202607050173.aspx
- 中央社科技分類頁，2026-07-05 查核；確認當日科技分類最新稿件時間，主卡改採同日 X Money 金融科技新聞。
  https://www.cna.com.tw/list/ait.aspx
"""
    manifest = {
        "date": "2026-07-05",
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
        ("cover", "2026.07.05", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "週日也不能亂傳", ["今天 4 則重點一次看", "颱風、食安、槍擊、金融科技", "先看來源，再決定轉不轉"]),
        ("taiwan_typhoon_bavi", "台灣天氣", "強颱巴威 10、11 日最近", "侵襲新竹以北、宜花機率逾 4 成", "先別囤泡麵，先看路徑", ["氣象署估海警機會高", "10、11 日全台有雨", "中南部及東半部山區防豪雨"]),
        ("taiwan_food_oil", "台灣生活", "中聯油品 257 業者受影響", "7 日傍晚公布第一波產品名單", "不是每瓶油都中，但要看清楚", ["第 1 層產品已要求下架", "20% 以上加工品 7/6 前下架", "20% 以下須主動揭露資訊"]),
        ("international_brooklyn", "國際焦點", "紐約國慶夜槍擊 8 人中槍", "布魯克林科尼島，含 4 名孩童", "煙火之外，槍聲也太真實", ["警方晚間 10:37 獲報", "7 人穩定、1 女子危急", "現場查獲槍械，暫無逮捕"]),
        ("tech_x_money", "科技新梗", "X Money 想把社群變銀行", "美國部分付費會員已先開放", "滑一滑，錢也滑走了", ["可轉帳、存款與支付", "合作 Visa 與 Cross River Bank", "下一站鎖定日本市場"]),
        ("summary", "今日總結", "今天大概是這樣", "週日版：颱風、食安、國際、金融科技", "可以笑，但不要亂傳", ["台灣：巴威路徑＋油品名單", "國際：美國國慶夜槍擊", "科技：X Money 超級 App 野心"]),
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
