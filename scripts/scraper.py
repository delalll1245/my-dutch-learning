import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_news():
    # 我們以 De Standaard 為例 (這裡示範抓取一篇文章)
    url = "https://www.standaard.be/nieuws/hoe-leer-ik-het-efficientst-een-nieuwe-taal/41667623.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('h1').text.strip() if soup.find('h1') else "No Title"
        # 抓取內文段落
        paragraphs = soup.find_all('p')
        content = "\n".join([p.text for p in paragraphs[:5]]) # 先抓前5段避免太長
        
        new_data = {
            "title": title,
            "url": url,
            "content": content,
            "date": "2026-01-05"
        }
        
        # 儲存到 data/news.json
        with open('data/news.json', 'w', encoding='utf-8') as f:
            json.dump([new_data], f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error scraping: {e}")

if __name__ == "__main__":
    scrape_news()
