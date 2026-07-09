from pathlib import Path
import json
import shutil
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import render_2026_07_08 as base


SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-09"
OUT = DAILY / "cards"


def write_text_files(cards):
    caption = """# Caption

今晚新聞梗圖包來了。

今天整理 2026/07/09 台灣時間可查核的重點：強颱巴威海警發布，台東、蘭嶼已出現 7 公尺巨浪，10 日凌晨至清晨可能發布陸警；中聯油品食安案擴大處置，4 至 6 月相關油品食品須在 10 日中午前下架；美伊衝突再升溫，美軍再度空襲伊朗；科技線則是中國傳擬放行頂尖 AI 公司採購少量輝達 H200。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #颱風巴威 #強烈颱風 #中聯油品 #食安 #美伊衝突 #伊朗 #輝達 #NVIDIA #H200 #AI晶片 #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-09（台灣時間）

- 中央社，2026-07-09 18:05／18:55 更新，〈颱風巴威來勢洶洶 台東、蘭嶼現7公尺巨浪〉
  https://www.cna.com.tw/news/ahel/202607090288.aspx
- 中央社，2026-07-09 14:32／14:45 更新，〈颱風巴威海上警報發布 暴風半徑維持380公里〉
  https://www.cna.com.tw/news/ahel/202607090168.aspx
- 中央社，2026-07-09 15:25／17:11 更新，〈中聯油品案 卓榮泰指示擴大下架、修法、簡化退貨〉
  https://www.cna.com.tw/news/aipl/202607090190.aspx
- 中央社，2026-07-09 14:20，〈中聯油品案 石崇良：修法強化高風險產品檢驗頻率〉
  https://www.cna.com.tw/news/aipl/202607090163.aspx
- 中央社，2026-07-09 02:30／14:22 更新，〈川普淡化美伊升溫局勢 稱衝突很快就會結束〉
  https://www.cna.com.tw/news/aopl/202607090009.aspx
- 中央社全球視野，2026-07-09，〈川普拋震撼彈！宣布停戰協議喊卡 美軍再猛轟伊朗〉
  https://www.cna.com.tw/video/globalview/4355234
- 中央社，2026-07-09 00:52，〈美媒：中國擬允許頂尖AI公司 採購少量輝達H200晶片〉
  https://www.cna.com.tw/news/aopl/202607090005.aspx
"""
    manifest = {
        "date": "2026-07-09",
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
        ("cover", "2026.07.09", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "先看來源，再決定轉發", ["今天 4 則重點一次看", "颱風、食安、美伊、AI晶片", "可以有梗，但不能亂講"]),
        ("taiwan_typhoon_bavi", "台灣天氣", "巴威海警發布 風浪先到", "台東、蘭嶼已觀測 7 公尺巨浪", "先收陽台，再問放假", ["七級風暴風半徑 380 公里", "最快 10 日凌晨至清晨發陸警", "10 晚至 11 日影響最劇烈"]),
        ("taiwan_food_oil", "台灣生活", "中聯油品案擴大下架", "4 至 6 月相關油品食品限期下架", "先看清單，再開火", ["10 日中午前全數預防性下架", "政院提修法、簡化退貨等 5 指示", "中聯釐清前無期限停工"]),
        ("international_iran_us", "國際焦點", "美伊衝突又升溫", "美軍再空襲，川普稱很快會結束", "遠方戰火，油價先懂", ["中央社列美軍再度猛烈空襲", "伊朗沿海多地傳爆炸聲", "波灣與能源安全仍受關注"]),
        ("tech_ai_h200", "科技新梗", "中國傳放行輝達 H200", "頂尖 AI 公司可望少量採購", "晶片不是買菜，還要寫理由", ["阿里、字節、DeepSeek 被點名", "用途傳限於 AI 訓練", "總量可能低於 20 萬枚"]),
        ("summary", "今日總結", "今天大概是這樣", "週四版：颱風、食安、美伊、AI 晶片", "可以笑，但不要亂傳", ["台灣：巴威海警＋油品下架", "國際：美伊交火牽動能源安全", "科技：H200 消息牽動 AI 供應鏈"]),
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
