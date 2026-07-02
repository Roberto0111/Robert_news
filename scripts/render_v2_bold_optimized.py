from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path("/Users/roberto/Documents/Codex/2026-07-02/new-chat-2")
SRC = ROOT / "outputs" / "daily_ig_news" / "2026-07-02_personalized_full"
OUT = ROOT / "outputs" / "daily_ig_news" / "2026-07-02_personalized_full_v2_bold_optimized"

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

    # Keep v2's stable card style, but make it feel more intentional and readable.
    rr(d, (48, 42, 1032, 222), 34, (255, 255, 255, 222), width=5)
    tag_f = font(32)
    title_f = fit(d, spec["title"], 845, spec.get("title_size", 59), 34)
    sub_f = fit(d, spec["subtitle"], 810, 30, 22)

    rr(d, (78, 70, 78 + tw(d, spec["tag"], tag_f) + 38, 120), 23, (255, 213, 70, 250), width=4)
    bold(d, (97, 76), spec["tag"], tag_f, fill=(224, 63, 47, 255), stroke=0)
    bold(d, (82, 124), spec["title"], title_f, stroke=1)
    bold(d, (84, 182), spec["subtitle"], sub_f, fill=(20, 128, 132, 255), stroke=0)

    # Bottom panel is a touch lower and cleaner, with stronger type and less visual noise.
    rr(d, (84, 1130, 996, 1304), 30, (255, 255, 255, 226), width=5)
    bullet_f = font(33)
    y = 1151
    for bullet in spec["bullets"]:
        d.ellipse((112, y + 8, 136, y + 32), fill=(255, 213, 70, 255), outline=(31, 35, 38, 255), width=3)
        lines = wrap(d, bullet, bullet_f, 785)
        bold(d, (154, y - 1), lines[0], bullet_f, stroke=1)
        y += 44

    # Smaller punch sticker avoids covering the host's hands/body as much.
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
        shutil.copy2(p, OUT / p.name)

    specs = [
        ("cover", "2026.07.02", "今晚 8 點新聞梗圖包", "你的卡通主播｜台灣＋國際＋科技", "先不要急，看完再急", ["今天 5 則重點一次看", "迷因感可以有，事實不能亂飛", "來源先放好，轉發比較安心"]),
        ("taiwan_island_policy", "台灣時事", "離島建設第 7 期 56 億拍板", "政院核定 2026-2029 實施方案", "離島不是遠，是預算要到", ["交通、民生、公共服務是重點", "56 億是總經費，不是直接發錢", "影響旅遊、物流、地方生活品質"]),
        ("taiwan_food_safety", "台灣生活", "沙拉油風波 退款名單出爐", "泰山公布 4 至 6 月 10 品項可退款", "先翻廚房，不是翻白眼", ["問題油品波及通路與部分餐飲", "部分業者稱僅用於員工餐廳", "買過相關品項：留發票、看公告"]),
        ("international_us_jobs", "國際財經", "美國就業降溫 市場先鬆口氣", "6 月非農新增 5.7 萬，低於預期", "數字不好看，市場反而笑一下", ["就業變弱牽動利率預期", "美股開盤微幅走高", "台股、匯率、科技股情緒會受影響"]),
        ("tech_gaming", "科技新梗", "PS 實體光碟 傳 2028 走入歷史", "數位下載時代，玩家收藏感要變了", "盒子沒了，錢包還在痛", ["平台往數位下載走更快", "二手交易、借片、收藏都可能受影響", "買的是遊戲，還是使用權？"]),
        ("summary", "今日總結", "今天大概是這樣", "迷因感可以有，來源一定要留", "可以笑，但不要亂傳", ["台灣：離島建設＋食安退款", "國際：美國就業數字牽動市場", "科技：實體遊戲片時代可能縮小"]),
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
    sheet.save(OUT / "contact_sheet.png", quality=95)

    for p in outs:
        print(p, Image.open(p).size)
    print(OUT / "contact_sheet.png")


if __name__ == "__main__":
    main()
