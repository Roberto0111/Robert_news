from pathlib import Path
import json
import shutil
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import render_2026_07_08 as base


SRC = ROOT / "templates"
DAILY = ROOT / "daily" / "2026-07-12"
OUT = DAILY / "cards"


def write_text_files(cards):
    caption = """# Caption

今晚新聞梗圖包來了。

今天整理 2026/07/12 台灣時間可查核的重點：颱風巴威警報上午 8:30 解除，但全國災情仍累計 3004 件、134 人受傷，萬里溪堰塞湖續列戒備；中聯油品事件擴大，3 批號異常，受影響油品回收與重新上架原則持續更新；國際線看伊朗再度宣布關閉荷莫茲海峽，能源與航運風險升溫；科技產經線則是台積電嘉義科學園區二期再設 3 座先進封裝廠，AI 供應鏈繼續擴張。

迷因感可以有，來源一定要留。先看懂，再決定要不要轉發。

#Hashtags

#今日新聞 #台灣時事 #國際新聞 #科技新聞 #新聞懶人包 #台灣迷因 #颱風巴威 #災後復原 #中聯油品 #食安 #荷莫茲海峽 #伊朗 #台積電 #先進封裝 #CoWoS #DailyNews
"""
    sources = """# Sources

查核日期：2026-07-12（台灣時間）

- 中央社聚焦頁，2026-07-12 晚間查核；確認當日熱門排序包含颱風巴威災情、預防性下架油品、南海與美伊情勢、台積電先進封裝等新聞。
  https://www.cna.com.tw/list/headlines.aspx
- 中央社，2026-07-12 08:22／12:47 更新，〈颱風巴威遠離 氣象署上午8時30分解除警報〉
  https://www.cna.com.tw/news/ahel/202607120012.aspx
- 中央社，2026-07-12 11:08／11:30 更新，〈颱風巴威全國災情3004件134傷 萬里溪堰塞湖估15日滿水溢流〉
  https://www.cna.com.tw/news/asoc/202607120044.aspx
- 中央社，2026-07-12 17:32／19:37 更新，〈預防性下架油品 食藥署7/13公布重新上架原則〉
  https://www.cna.com.tw/news/ahel/202607120155.aspx
- 衛生福利部食品藥物管理署中聯油脂案專區，2026-07-12 查核；確認4月至6月相關油品預防性下架、三批號異常與追查進度。
  https://www.fda.gov.tw/tc/siteList.aspx?sid=13712
- 中央社，2026-07-12 13:21／14:16 更新，〈防堵食安漏洞 衛福部擬重罰隱匿、導入專業獨董〉
  https://www.cna.com.tw/news/ahel/202607120085.aspx
- 中央社，2026-07-12 08:00，〈伊朗再關荷莫茲海峽 警告報復行動將遭嚴厲回應〉
  https://www.cna.com.tw/news/aopl/202607120011.aspx
- 中央社，2026-07-12 13:15／14:24 更新，〈嘉科二期台積電再設3座廠 打造全球先進封裝重鎮〉
  https://www.cna.com.tw/news/afe/202607120083.aspx
- 中央社，2026-07-12 10:53／11:03 更新，〈台積電CoWoS供不應求 封測台廠、英特爾受惠訂單外溢〉
  https://www.cna.com.tw/news/afe/202607120038.aspx
"""
    manifest = {
        "date": "2026-07-12",
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
        ("cover", "2026.07.12", "今晚 8 點新聞梗圖包", "台灣＋國際＋科技｜來源先放好", "先看來源，再決定轉發", ["今天 4 則重點一次看", "巴威、油品、荷莫茲、封裝", "可以有梗，但不能亂講"]),
        ("taiwan_typhoon_bavi", "台灣天氣", "巴威警報解除 災情續算", "3004件災情、134傷｜堰塞湖戒備", "風走了，善後才上班", ["氣象署8:30解除颱風警報", "災情多為路樹與民生設施", "萬里溪堰塞湖估15日溢流"]),
        ("taiwan_food_oil", "台灣生活", "中聯油品 3批號異常", "58品項受影響，7/13公布上架原則", "先別急著回鍋", ["4至6月29批次全面下架", "截至上午已回收144公噸", "衛福部研議重罰隱匿"]),
        ("international_hormuz", "國際焦點", "荷莫茲再關 航線拉警報", "伊朗稱封鎖至另行通知", "不是遠方，是油輪路口", ["伊朗稱外國勢力威脅安全", "警告敵方基地成攻擊目標", "能源與航運風險再升溫"]),
        ("tech_tsmc_chiayi", "科技產經", "嘉科二期再設3座廠", "台積電先進封裝，AI供應鏈加速", "晶片很小，園區很忙", ["嘉科一期先進封裝已量產", "二期基地約90公頃動土", "封測台廠吃到訂單外溢"]),
        ("summary", "今日總結", "今天大概是這樣", "週日版：巴威、食安、荷莫茲、先進封裝", "可以笑，但不要亂傳", ["台灣：巴威善後＋油品下架", "國際：荷莫茲海峽再升溫", "科技：先進封裝需求爆量"]),
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
