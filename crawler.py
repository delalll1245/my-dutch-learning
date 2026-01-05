import requests
from bs4 import BeautifulSoup
import json
import os
import csv # 💡 新增：處理 CSV 必備
from io import StringIO # 💡 新增：處理文字串流

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_soup(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        res.encoding = 'utf-8'
        return BeautifulSoup(res.text, 'html.parser')
    except Exception as e:
        print(f"無法連線至 {url}: {e}")
        return None

# --- 1. 自動巡邏網站邏輯 (保持原有逻辑，增加防呆) ---

def scrape_wablieft():
    url = "http://www.wablieft.be/nl/krant"
    soup = get_soup(url)
    results = []
    if soup:
        for item in soup.select('.views-row')[:3]: 
            link_tag = item.select_one('h2 a')
            if link_tag:
                results.append({
                    "title": link_tag.get_text(strip=True),
                    "url": "http://www.wablieft.be" + link_tag['href'],
                    "source": "Wablieft (Easy)",
                    "content": "專為學習者設計的簡化新聞。"
                })
    return results

def scrape_metro():
    url = "https://nl.metrotime.be/onspanning"
    soup = get_soup(url)
    results = []
    if soup:
        # ⚠️ Metro 的選取器很常換，如果跑不動請檢查此處
        for item in soup.select('article')[:3]:
            title_tag = item.select_one('h2')
            link_tag = item.select_one('a')
            if title_tag and link_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "url": link_tag['href'] if link_tag['href'].startswith('http') else "https://nl.metrotime.be" + link_tag['href'],
                    "source": "Metrotime",
                    "content": "來自 Metro 的最新生活與時事。"
                })
    return results

def scrape_zinin():
    url = "https://zininnederlands.be/"
    soup = get_soup(url)
    results = []
    if soup:
        for item in soup.select('.post-title')[:3]:
            link_tag = item.select_one('a')
            if link_tag:
                results.append({
                    "title": link_tag.get_text(strip=True),
                    "url": link_tag['href'],
                    "source": "Zin in Nederlands",
                    "content": "荷蘭語學習技巧與日常用法。"
                })
    return results

def scrape_nedbox():
    url = "https://www.nedbox.be/nieuws"
    soup = get_soup(url)
    results = []
    if soup:
        for item in soup.select('.views-row')[:3]:
            title_tag = item.select_one('.field-content a')
            if title_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "url": "https://www.nedbox.be" + title_tag['href'],
                    "source": "NedBox",
                    "content": "互動式學習新聞內容。"
                })
    return results

# --- 2. 妳的 Google 試算表手動資料庫 (重大修正) ---

def scrape_google_sheet():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSyPZtfBk2ED0-JBkhF0hTstrvp67v6sr5ndwAGQT8miCARIm1Bi5otqE58noyso-5Psewp4H4Q4Ogu/pub?output=csv"
    results = []
    try:
        res = requests.get(csv_url, timeout=10)
        res.encoding = 'utf-8'
        
        # 💡 改用 csv.reader 讀取，避免逗號導致資料切碎
        f = StringIO(res.text)
        reader = csv.reader(f)
        next(reader) # 跳過第一列標題
        
        for row in reader:
            if len(row) >= 4:
                results.append({
                    "title": row[0].strip(),
                    "url": row[1].strip(),
                    "source": row[2].strip() or "Kelsey 精選",
                    "content": row[3].strip()
                })
    except Exception as e:
        print(f"Google 試算表讀取失敗: {e}")
    return results

# --- 總整合執行 ---

def main():
    print("嘟仔巡邏隊出動！")
    final_news = []
    
    # 抓取並合併資料
    final_news.extend(scrape_wablieft())
    final_news.extend(scrape_metro())
    final_news.extend(scrape_zinin())
    final_news.extend(scrape_nedbox())
    final_news.extend(scrape_google_sheet())
    
    # 過濾掉空的內容
    final_news = [n for n in final_news if n['title']]
    
    os.makedirs('data', exist_ok=True)
    
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(final_news, f, ensure_ascii=False, indent=4)
    
    print(f"成功更新！現在共有 {len(final_news)} 則新聞資料。")

if __name__ == "__main__":
    main()
