#!/usr/bin/env python3
from pathlib import Path
import json, os, datetime, shutil
from typing import List, Dict

class SiteGenerator:
    def __init__(self, data_dir="data", output_dir="docs", templates_dir="templates"):
        self.data_dir, self.output_dir, self.templates_dir = map(Path, [data_dir, output_dir, templates_dir])
        self.news_data = []
        
    def load_news_data(self) -> bool:
        try:
            # Solo cargar noticias del día actual
            today = datetime.date.today().strftime('%Y-%m-%d')
            today_file = self.data_dir / f"news_{today}.json"
            
            if today_file.exists():
                data = json.load(open(today_file, 'r', encoding='utf-8'))
                self.news_data = data.get('news', [])
                print(f"📰 Cargadas {len(self.news_data)} noticias de hoy ({today})")
                return bool(self.news_data)
            else:
                print(f"❌ No se encontró archivo de noticias para hoy ({today})")
                return False
        except Exception as e:
            print(f"Error loading news data: {e}")
            return False
    
    def load_template(self, name: str) -> str:
        try:
            return open(self.templates_dir / name, 'r', encoding='utf-8').read()
        except Exception as e:
            print(f"Error loading template {name}: {e}")
            return ""
    
    def generate_news_card(self, news: Dict, index: int) -> str:
        template = self.load_template("news_card.html")
        if not template:
            return ""
            
        description = news.get('description', ' '.join(news.get('content', '').replace('**', '').replace('*', '').replace('[', '').replace(']', '').split()[:25]))
        description = description[:180] + "..." if len(description) > 180 else description
        
        thumbnail_html = f'<div class="news-card-image"><img src="{news.get("thumbnail")}" alt="{news.get("title", "News")}" loading="lazy"></div>' if news.get('thumbnail') else ""
        time_html = f'<div class="news-time">{news.get("time")}</div>' if news.get('time') else ''
        time_meta = f' • <strong>Hora:</strong> {news.get("time")}' if news.get('time') else ''
        
        replacements = {
            '{{THUMBNAIL_HTML}}': thumbnail_html,
            '{{NEWS_ID}}': str(index + 1),
            '{{CATEGORY}}': news.get('category', 'General'),
            '{{TIME_HTML}}': time_html,
            '{{LINK}}': news.get('link', '#'),
            '{{TITLE}}': news.get('title', 'Sin título'),
            '{{DESCRIPTION_HTML}}': f'<div class="news-description"><p>{description}</p></div>' if description else '',
            '{{DATE}}': news.get('date', 'N/A'),
            '{{TIME_META}}': time_meta
        }
        
        result = template
        for k, v in replacements.items():
            result = result.replace(k, v)
        return result
    
    def generate_site(self) -> bool:
        try:
            if not self.load_news_data():
                return False
                
            self.output_dir.mkdir(exist_ok=True)
            if (css_source := self.templates_dir / "styles.css").exists():
                shutil.copy2(css_source, self.output_dir / "styles.css")
            
            today = datetime.date.today()
            news_cards = ''.join(self.generate_news_card(news, i) for i, news in enumerate(self.news_data[:50]))
            
            template = self.load_template("index.html")
            html_content = template.replace('{{TITLE}}', 'Diario Digital - Noticias del Perú')\
                                 .replace('{{DESCRIPTION}}', 'Noticias diarias extraídas automáticamente del Diario Correo')\
                                 .replace('{{LAST_UPDATE}}', f'Última actualización: {today.strftime("%d de %B de %Y")}')\
                                 .replace('{{TOTAL_NEWS}}', str(len(self.news_data)))\
                                 .replace('{{TOTAL_CATEGORIES}}', str(len({n.get('category', 'General') for n in self.news_data})))\
                                 .replace('{{NEWS_CARDS}}', news_cards)\
                                 .replace('{{CURRENT_YEAR}}', str(today.year))
            
            open(self.output_dir / "index.html", 'w', encoding='utf-8').write(html_content)
            return True
            
        except Exception as e:
            print(f"Error generating website: {e}")
            return False

if __name__ == "__main__":
    import sys
    sys.exit(0 if SiteGenerator().generate_site() else 1)
