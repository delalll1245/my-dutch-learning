import requests
from bs4 import BeautifulSoup
import json
import os

# 設定 Header 避免被網站阻擋
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

# --- 各個網站的專屬抓取邏輯 ---

def scrape_wablieft():
    """抓取 Wablieft (學習者友善新聞)"""
    url = "http://www.wablieft.be/nl/krant"
    soup = get_soup(url)
    results = []
    if soup:
        # 抓取文章區塊 (根據該站結構抓取標題與網址)
        for item in soup.select('.views-row')[:3]: 
            link_tag = item.select_one('h2 a')
            if link_tag:
                results.append({
                    "title": link_tag.get_text(strip=True),
                    "url": "http://www.wablieft.be" + link_tag['href'],
                    "source": "Wablieft (Easy)",
                    "content": "專為荷蘭語學習者設計的簡化新聞內容。"
                })
    return results

def scrape_metro():
    """抓取 Metro (生活化新聞)"""
    url = "https://nl.metrotime.be/onspanning"
    soup = get_soup(url)
    results = []
    if soup:
        for item in soup.select('article')[:3]:
            title_tag = item.select_one('h2')
            link_tag = item.select_one('a')
            if title_tag and link_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "url": link_tag['href'] if link_tag['href'].startswith('http') else "https://nl.metrotime.be" + link_tag['href'],
                    "source": "Metrotime",
                    "content": "來自 Metro 的最新生活與娛樂動態。"
                })
    return results

def scrape_zinin():
    """抓取 Zin in Nederlands (學習部落格)"""
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
                    "content": "實用的荷蘭語學習技巧與日常用法。"
                })
    return results

def scrape_nedbox():
    """抓取 NedBox (互動式學習新聞)"""
    url = "https://www.nedbox.be/nieuws"
    soup = get_soup(url)
    results = []
    if soup:
        # NedBox 結構較複雜，通常抓取其最新消息區塊
        for item in soup.select('.views-row')[:3]:
            title_tag = item.select_one('.field-content a')
            if title_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "url": "https://www.nedbox.be" + title_tag['href'],
                    "source": "NedBox",
                    "content": "結合影音與互動練習的荷蘭語新聞。"
                })
    return results

# --- 總整合執行 ---

def main():
    print("開始巡邏荷蘭語新聞...")
    final_news = []
    
    # 輪流執行各個爬蟲函數
    final_news.extend(scrape_wablieft())
    final_news.extend(scrape_metro())
    final_news.extend(scrape_zinin())
    final_news.extend(scrape_nedbox())
    
    # 確保資料夾存在
    os.makedirs('data', exist_ok=True)
    
    # 存檔為 JSON
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(final_news, f, ensure_ascii=False, indent=4)
    
    print(f"成功更新！共抓取 {len(final_news)} 則新聞。")

if __name__ == "__main__":
    main()
