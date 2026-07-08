from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-08"
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

今天整理 2026/07/08 台灣時間可查核的重點：強颱巴威暴風圈估涵蓋半個台灣，氣象署預計 9 日發布海陸警；中聯油品追查延燒，南僑再製 7 項油品流向北市 62 店；美伊停火被稱結束，中東危機推升油價逾 5%；AI 伺服器需求旺，緯創、英業達 6 月營收創高。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #颱風巴威 #中聯油品 #南僑油脂 #食安 #美伊戰爭 #油價 #AI伺服器 #緯創 #英業達 #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-08（台灣時間）

- 中央社首頁／即時新聞，2026-07-08 查核；確認當日晚間熱門排序包含巴威颱風、中聯油品、美伊衝突、AI 與電子代工新聞。
  https://www.cna.com.tw/
- 中央社，2026-07-08 17:41／19:04 更新，〈颱風巴威暴風圈估涵蓋半個台灣 9日將發海陸警〉
  https://www.cna.com.tw/news/ahel/202607080301.aspx
- 交通部中央氣象署颱風消息，2026-07-08 查核；確認強烈颱風巴威現況與中心氣壓、風速、暴風半徑資訊。
  https://www.cwa.gov.tw/V8/C/P/Typhoon/TY_NEWS.html
- 中央社，2026-07-08 19:29／19:48 更新，〈北市：南僑再製油流向全聯、胖老爹、錢櫃、好樂迪等62店〉
  https://www.cna.com.tw/news/aloc/202607080358.aspx
- 中央社，2026-07-08 17:32，〈川普稱伊朗停火結束 油價飆漲逾5%〉
  https://www.cna.com.tw/news/aopl/202607080295.aspx
- 中央社全球視野，2026-07-08，〈伊朗宣稱報復襲擊美軍設施 科威特巴林空襲警報大作〉
  https://www.cna.com.tw/video/news/4355224
- 中央社，2026-07-08 19:45，〈緯創6月營收寫單月次高 英業達首破千億元創新高〉
  https://www.cna.com.tw/news/afe/202607080362.aspx
"""
    manifest = {
        "date": "2026-07-08",
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
        ("cover", "2026.07.08", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "先看來源，再決定轉發", ["今天 4 則重點一次看", "颱風、食安、中東、AI伺服器", "可以有梗，但不能亂講"]),
        ("taiwan_typhoon_bavi", "台灣天氣", "巴威暴風圈估蓋半個台灣", "氣象署預計 9 日發布海陸警", "先收陽台，再問放假", ["7 級風暴風半徑達 380 公里", "10、11 日影響最顯著", "北部與東半部先做好防颱"]),
        ("taiwan_food_oil", "台灣生活", "問題油追到北市 62 店", "南僑再製 7 項油品流向曝光", "先看清單，再點炸物", ["全聯、胖老爹、錢櫃等上榜", "含量 20% 以下產品也全下架", "台北衛生局裁處南僑 300 萬"]),
        ("international_iran_oil", "國際焦點", "美伊停火被稱已結束", "中東攻擊升溫，油價飆逾 5%", "不是遠方，是油箱", ["布蘭特原油升至 78.09 美元", "西德州原油升至 74.23 美元", "科威特、巴林響起空襲警報"]),
        ("tech_ai_servers", "科技財經", "AI 伺服器撐起代工營收", "緯創單月次高，英業達首破千億", "AI 很熱，產線更熱", ["緯創 6 月營收 3218.22 億", "英業達 6 月營收 1022.62 億", "伺服器業務仍估逐季成長"]),
        ("summary", "今日總結", "今天大概是這樣", "週三版：颱風、食安、中東、AI 伺服器", "可以笑，但不要亂傳", ["台灣：巴威＋問題油流向", "國際：美伊衝突推升油價", "科技：AI 需求帶動代工廠"]),
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
