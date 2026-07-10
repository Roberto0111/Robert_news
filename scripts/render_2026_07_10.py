from pathlib import Path
import json
import shutil
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import render_2026_07_08 as base


SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-10"
OUT = DAILY / "cards"


def write_text_files(cards):
    caption = """# Caption

今晚新聞梗圖包來了。

今天整理 2026/07/10 台灣時間可查核的重點：颱風巴威陸警範圍擴大，暴風圈最快 11 日凌晨觸陸，20 縣市 11 日風雨預報達停班課標準；中聯油品案最新核實，4 至 6 月問題油量下修至 2.7 萬噸；中國朝「藍色大陸」中心試射飛彈，引發太平洋島國反彈，另宣布禁氦氣出口；科技產經線則是 AI 需求續熱，前 5 月電子零組件加班工時創 47 年同期最高。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #颱風巴威 #停班停課 #中聯油品 #食安 #中國試射飛彈 #太平洋島國 #氦氣 #AI #電子零組件 #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-10（台灣時間）

- 中央社即時新聞，2026-07-10 晚間查核；確認熱門與即時排序包含巴威颱風、中聯油品、中國試射飛彈、氦氣出口禁令、AI 與電子零組件新聞。
  https://www.cna.com.tw/list/aall.aspx
- 中央社，2026-07-10 18:15，〈颱風巴威陸警範圍增彰化馬祖 暴風圈最快11日凌晨觸陸〉
  https://www.cna.com.tw/news/ahel/202607100186.aspx
- 中央社，2026-07-10 16:37，〈颱風巴威襲台 20縣市11日風雨預報達停班課標準〉
  https://www.cna.com.tw/news/ahel/202607100147.aspx
- 中央社，2026-07-10 16:09，〈食藥署：與中聯福壽福懋泰山核實 4至6月問題油量下修至2.7萬噸〉
  https://www.cna.com.tw/news/ahel/202607100140.aspx
- 中央社，2026-07-10 19:04，〈中國朝「藍色大陸」中心試射飛彈 太平洋島國群起反彈〉
  https://www.cna.com.tw/news/aopl/202607100206.aspx
- 中央社，2026-07-10 18:55，〈卡達俄羅斯供應受限 中國宣布禁氦氣出口〉
  https://www.cna.com.tw/news/acn/202607100202.aspx
- 中央社，2026-07-10 17:33，〈AI續熱 前5月電子零組件加班工時創47年同期最高〉
  https://www.cna.com.tw/news/afe/202607100174.aspx
"""
    manifest = {
        "date": "2026-07-10",
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
        ("cover", "2026.07.10", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "先看來源，再決定轉發", ["今天 4 則重點一次看", "颱風、食安、飛彈、AI工時", "可以有梗，但不能亂講"]),
        ("taiwan_typhoon_bavi", "台灣天氣", "巴威陸警擴大 風雨逼近", "暴風圈最快 11 日凌晨觸陸", "先收陽台，再問放假", ["陸警範圍增彰化、馬祖", "20 縣市 11 日預報達停班課標準", "海運、交通與山區撤離陸續調整"]),
        ("taiwan_food_oil", "台灣生活", "中聯問題油量下修", "4 至 6 月核實為 2.7 萬噸", "先看清單，再開火", ["食藥署與中聯、福壽等核實", "部分縣市與通路持續下架回收", "買到疑似品項先留包裝發票"]),
        ("international_missile", "國際焦點", "中國試射飛彈惹議", "太平洋島國群起反彈", "飛得很遠，抗議更近", ["試射方向指向藍色大陸中心", "多國要求尊重區域和平安全", "南太平洋安全議題再升溫"]),
        ("tech_ai_overtime", "科技產經", "AI 熱到工時也創高", "電子零組件加班創 47 年同期高", "AI 很熱，產線更熱", ["前 5 月平均加班 20.3 小時", "AI 伺服器與高階晶片需求推升", "訂單熱度也反映在勞動數字"]),
        ("summary", "今日總結", "今天大概是這樣", "週五版：颱風、食安、國際安全、AI 工時", "可以笑，但不要亂傳", ["台灣：巴威陸警＋問題油追查", "國際：飛彈試射與氦氣管制", "科技：AI 需求推高加班工時"]),
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
