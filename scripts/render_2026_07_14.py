from pathlib import Path
import json
import shutil
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import render_2026_07_08 as base


SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-14"
OUT = DAILY / "cards"


def write_text_files(cards):
    caption = """# Caption

今晚新聞梗圖包來了。

今天整理 2026/07/14 台灣時間可查核的重點：西南風挾水氣，15 日大台北與西半部山區午後防局部大雨；中聯油脂案持續擴大，台中公布第 3 至 5 批第 2 層下游 165 家，7-ELEVEN 也啟動 APP 主動退費；國際線看美伊與荷莫茲海峽，封鎖、通行費與油價壓力一起升溫；科技產經線則是 AI 需求帶旺半導體供應鏈，上市櫃 6 月營收同步年增。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #西南風 #大雨 #中聯油脂 #食安 #7ELEVEN #荷莫茲海峽 #美伊戰爭 #油價 #AI供應鏈 #半導體 #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-14（台灣時間）

- 中央社首頁／即時新聞，2026-07-14 晚間查核；確認當日晚間首頁與即時新聞包含中聯油脂、西南風水氣、美伊／荷莫茲、AI 供應鏈等新聞。
  https://www.cna.com.tw/
- 中央社，2026-07-14 17:40／18:00 更新，〈西南風挾水氣 大台北、西半部山區15日防大雨〉
  https://www.cna.com.tw/news/ahel/202607140256.aspx
- 中央社，2026-07-14 19:02／19:40 更新，〈中市府公布中聯油脂下游業者 知名豆漿店、平價牛排受影響〉
  https://www.cna.com.tw/news/ahel/202607140287.aspx
- 中央社，2026-07-14 10:18／10:32 更新，〈中聯油品致癌物超標 食藥署：上下游都驗合格才能重上架〉
  https://www.cna.com.tw/news/ahel/202607140036.aspx
- 中央社，2026-07-14 18:20，〈統一超APP從簡退費 北市府籲各通路可比照辦理〉
  https://www.cna.com.tw/news/aloc/202607140272.aspx
- 中央社，2026-07-14 05:17／14:25 更新，〈美再對伊朗海上封鎖 川普美東時間16日發表全國演說〉
  https://www.cna.com.tw/news/aopl/202607140008.aspx
- 中央社，2026-07-14 16:11，〈推動立法管理荷莫茲海峽 伊朗國會提出法案〉
  https://www.cna.com.tw/news/aopl/202607140197.aspx
- 中央社，2026-07-14 19:09，〈美軍對伊朗作戰新增1人喪生 累計14死414傷〉
  https://www.cna.com.tw/news/aopl/202607140289.aspx
- 中央社，2026-07-14 18:35／18:56 更新，〈美襲伊朗油價漲幅擴大 低接買盤進場亞股多收漲〉
  https://www.cna.com.tw/news/afe/202607140280.aspx
- 中央社，2026-07-14 19:14，〈AI帶旺半導體供應鏈 上市櫃公司6月營收齊揚〉
  https://www.cna.com.tw/news/afe/202607140291.aspx
- 中央社，2026-07-14 12:53／18:25 更新，〈蘋果iOS 27公測版 Siri AI變聰明、支援舊機變快〉
  https://www.cna.com.tw/news/ait/202607140109.aspx
"""
    manifest = {
        "date": "2026-07-14",
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
        ("cover", "2026.07.14", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "先看來源，再決定轉發", ["今天 4 則重點一次看", "雨勢、食安、荷莫茲、AI供應鏈", "可以有梗，但不能亂講"]),
        ("taiwan_southwest_rain", "台灣天氣", "15日午後 局部大雨要防", "西南風挾水氣，花東縱谷防焚風", "雲很滿，排水也要滿", ["南部不定時短暫陣雨或雷雨", "大台北、西半部山區防局部大雨", "17日前年度大潮，低窪區留意"]),
        ("taiwan_food_oil", "台灣生活", "中聯油脂 下游名單再擴", "第3至5批第2層下游共165家", "問題油，不靠印象吃", ["第3層以下累計131家受影響", "日正豆漿、愛將、瓦城等列名", "原油52件、產品321件一週內驗"]),
        ("international_hormuz_oil", "國際焦點", "荷莫茲海峽 又拉高油價", "美伊互槓封鎖與20%通行費", "遠方開打，油箱先懂", ["美稱重啟對伊朗海上封鎖", "伊朗國會提海峽管理法案", "美軍伊朗作戰累計14死414傷"]),
        ("tech_ai_supply_chain", "科技產經", "AI 帶旺半導體供應鏈", "上市櫃6月營收同步年增", "AI很雲，營收很硬", ["上市6月營收5.2477兆 年增47.16%", "上櫃3519億 年增38%", "半導體、AI伺服器、通路受惠"]),
        ("summary", "今日總結", "今天大概是這樣", "週二版：雨勢、食安、油價、AI 供應鏈", "可以笑，但不要亂傳", ["台灣：西南風水氣＋中聯油品", "國際：荷莫茲牽動油價風險", "科技：AI需求推升供應鏈營收"]),
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
