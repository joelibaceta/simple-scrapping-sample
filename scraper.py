#!/usr/bin/env python3
import datetime
import json
import os
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

class NewsScraper:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)
    
    def scrape_news(self) -> List[Dict]:
        date = datetime.date.today()
        url = f"https://diariocorreo.pe/archivo/todas/{date.strftime('%Y-%m-%d')}/"
        self.driver.get(url)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        news_elements = soup.find_all('div', {'class': re.compile(r'story-item.*')})
        
        news_list = []
        seen_links = set()
        
        for story in news_elements:
            title_elem = story.find('a', {'class': re.compile(r'story-item__title.*')})
            if not title_elem:
                continue
                
            link = title_elem.get('href', '')
            if not link or link in seen_links:
                continue
                
            seen_links.add(link)
            news_list.append({
                'title': title_elem.get_text(strip=True),
                'link': f"https://diariocorreo.pe{link}" if not link.startswith('http') else link,
                'category': story.find('a', {'class': re.compile(r'story-item__section.*')}).get_text(strip=True) if story.find('a', {'class': re.compile(r'story-item__section.*')}) else 'General',
                'date': date.isoformat()
            })
        
        return news_list
    
    def save_news(self, news_list: List[Dict]):
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        filename = f"news_{datetime.date.today().strftime('%Y-%m-%d')}.json"
        
        with open(os.path.join(data_dir, filename), 'w', encoding='utf-8') as f:
            json.dump({'news': news_list}, f, ensure_ascii=False, indent=2)
    
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

if __name__ == "__main__":
    scraper = NewsScraper()
    news = scraper.scrape_news()
    scraper.save_news(news)
