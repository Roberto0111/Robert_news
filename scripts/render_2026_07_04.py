from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path("/Users/roberto/Documents/Codex/2026-07-02/new-chat-2/outputs/ig_daily_news_publisher")
SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-04"
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
        ("cover", "2026.07.04", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "週末也要看重點", ["今天 4 則重點一次看", "有梗可以，數字不要亂飛", "先看來源，再決定轉不轉"]),
        ("taiwan_phoenix_office", "台灣時事", "台灣將設鳳凰城辦事處", "美國務院：促進美台經濟關係", "半導體搬家，窗口也跟上", ["亞利桑納台商與僑民增加", "台積電供應鏈聚落成重點", "籌備中，還不是明天開門"]),
        ("taiwan_food_oil", "台灣生活", "泰山油品 4 大流向公布", "連鎖賣場與業者下架 54 公噸", "先查油桶，不要先吵架", ["中聯原料供泰山約 291 公噸", "主要通路庫存已全數下架", "衛生局續追問題產品流向"]),
        ("international_heatwave", "國際焦點", "歐洲熱浪 4.1 億人受影響", "比利時超額死亡初估 1222 人", "不是熱一下，是熱到出事", ["6/15 至 6/30 多地飆 35 度", "比利時死亡數高出正常 39%", "極端高溫已是公共衛生題"]),
        ("tech_meta_ai_agents", "科技新梗", "Meta AI 代理進展慢半拍", "祖克柏坦言重組時機判斷失準", "AI 很會畫餅，老闆也會胃痛", ["5 月裁員並轉調約 7000 人", "今年 AI 基建投資最高 1450 億美元", "3 至 6 個月後再看成果"]),
        ("summary", "今日總結", "今天大概是這樣", "週末版：食安、外交、熱浪、AI", "可以笑，但不要亂傳", ["台灣：鳳凰城辦事處＋油品流向", "國際：歐洲熱浪牽動公衛風險", "科技：Meta AI 投資壓力上桌"]),
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

    for p in outs:
        print(p, Image.open(p).size)
    print(DAILY / "contact_sheet.png")


if __name__ == "__main__":
    main()
