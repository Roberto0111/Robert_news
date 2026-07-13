from pathlib import Path
import json
import shutil
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import render_2026_07_08 as base


SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-13"
OUT = DAILY / "cards"


def write_text_files(cards):
    caption = """# Caption

今晚新聞梗圖包來了。

今天整理 2026/07/13 台灣時間可查核的重點：巴威過後萬里溪堰塞湖水位逼近可能溢流口，農業部維持黃色警戒；中聯油脂案延燒，政院要求 1 週內完成檢驗、提出食安法修法，預防性下架產品採三原則把關後才能重新上架；國際線看曼谷酒吧大火，死亡人數增至 32 人、73 人受傷；科技產經線則是光寶科技宣布 9.19 億美元投資德州麥金尼，搶 AI 基礎設施與能源市場。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #颱風巴威 #萬里溪堰塞湖 #中聯油脂 #食安 #曼谷大火 #光寶科技 #AI基礎設施 #能源市場 #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-13（台灣時間）

- 中央社首頁／即時新聞，2026-07-13 晚間查核；確認當日晚間首頁與即時新聞包含中聯油脂、萬里溪堰塞湖、曼谷大火、光寶德州投資等新聞。
  https://www.cna.com.tw/
- 中央社，2026-07-13 19:12／19:26 更新，〈農業部：萬里溪堰塞湖水位近溢流口 維持黃色警戒〉
  https://www.cna.com.tw/news/ahel/202607130290.aspx
- 中央社，2026-07-13 17:52／18:16 更新，〈中聯油脂案 卓榮泰：1週內完成檢驗、提食安法修法〉
  https://www.cna.com.tw/news/aipl/202607130255.aspx
- 中央社，2026-07-13 10:42／13:56 更新，〈衛福部：9日起驗預防性下架油品 將公布重上架原則〉
  https://www.cna.com.tw/news/aipl/202607130049.aspx
- 中央社，2026-07-13 08:55／09:03 更新，〈福壽2產品使用中聯問題油延遲通報 中市府再罰600萬〉
  https://www.cna.com.tw/news/ahel/202607130022.aspx
- 中央社，2026-07-13 19:32，〈曼谷酒吧大火 增至32死73傷〉
  https://www.cna.com.tw/news/aopl/202607130299.aspx
- 中央社，2026-07-13 19:01／19:18 更新，〈曼谷啤酒餐廳大火死傷慘重 分析：裝潢材料易燃、濃煙致命〉
  https://www.cna.com.tw/news/aopl/202607130287.aspx
- 中央社，2026-07-13 18:04，〈光寶投資9.19億美元 德州麥金尼設立營運製造基地〉
  https://www.cna.com.tw/news/afe/202607130260.aspx
- 中央社，2026-07-13 15:44／15:56 更新，〈AI新戰場在太空 台灣學者加拿大創業布局衛星通訊〉
  https://www.cna.com.tw/news/ait/202607130186.aspx
"""
    manifest = {
        "date": "2026-07-13",
        "style": "personalized_full_v2_bold_optimized",
        "size": "1080x1350",
        "cards": [f"cards/{card.name}" for card in cards],
        "caption": "caption.md",
        "sources": "sources.md",
    }
    DAILY.mkdir(parents=True, exist_ok=True)
    (DAILY / "caption.md").write_text(caption, encoding="utf-8")
    (DAILY / "sources.md").write_text(sources, encoding="utf-8")
    (DAILY / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    base.DAILY = DAILY
    base.OUT = OUT
    OUT.mkdir(parents=True, exist_ok=True)

    sources = [
        SRC / "source_cover.png",
        SRC / "source_island_policy.png",
        SRC / "source_food_safety.png",
        SRC / "source_us_jobs.png",
        SRC / "source_tech_gaming.png",
        SRC / "source_summary.png",
    ]
    for source in sources:
        shutil.copy2(source, DAILY / source.name)

    specs = [
        ("cover", "2026.07.13", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "先看來源，再決定轉發", ["今天 4 則重點一次看", "堰塞湖、食安、曼谷、AI 基建", "可以有梗，但不能亂講"]),
        ("taiwan_wanli_landslide_lake", "台灣天氣", "堰塞湖近溢流 黃色警戒", "萬里溪水位距可能溢流口約 3.84 公尺", "水還沒滿，警覺先滿", ["農業部13日下午開應變會議", "蓄水約444.09萬立方公尺", "距溢流前12小時將發紅色警戒"]),
        ("taiwan_food_oil", "台灣生活", "中聯油脂案 一週內檢驗", "下架品重上架採三原則把關", "先別急著倒回鍋", ["21批樣本持續加速檢驗", "5批下游產品檢驗超標", "合格後才可恢復上架販售"]),
        ("international_bangkok_fire", "國際焦點", "曼谷酒吧大火 32死73傷", "專家：濃煙、有毒氣體與逃生困難致命", "不是火小，是出口太遠", ["事發於曼谷恰圖恰區酒吧", "25人仍在加護病房治療", "6名傷者身分仍待查明"]),
        ("tech_liteon_texas", "科技產經", "光寶德州投資 9.19 億美元", "麥金尼設製造營運基地，搶 AI 基建", "AI 很雲，工廠很實", ["基地面積逾65萬平方英尺", "預計創造超過600個工作", "鎖定北美能源與AI需求"]),
        ("summary", "今日總結", "今天大概是這樣", "週一版：災後監測、食安、曼谷、AI 基建", "可以笑，但不要亂傳", ["台灣：堰塞湖警戒＋油品檢驗", "國際：曼谷大火傷亡擴大", "科技：光寶加碼北美製造"]),
    ]
    specs = [
        {"slug": slug, "tag": tag, "title": title, "subtitle": subtitle, "punch": punch, "bullets": bullets}
        for slug, tag, title, subtitle, punch, bullets in specs
    ]
    cards = [base.overlay(source, spec, idx) for idx, (source, spec) in enumerate(zip(sources, specs), 1)]

    thumbs = [Image.open(card).resize((180, 225), Image.LANCZOS) for card in cards]
    sheet = Image.new("RGB", (180 * len(thumbs), 225), (245, 245, 240))
    for idx, thumb in enumerate(thumbs):
        sheet.paste(thumb, (180 * idx, 0))
    sheet.save(DAILY / "contact_sheet.png", quality=95)
    write_text_files(cards)

    for card in cards:
        print(card, Image.open(card).size)
    print(DAILY / "contact_sheet.png")


if __name__ == "__main__":
    main()
