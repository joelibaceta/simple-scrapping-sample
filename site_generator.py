#!/usr/bin/env python3
"""
Generador de sitio web estático para el diario de noticias
Convierte archivos JSON de noticias en un hermoso sitio web tipo periódico
"""

import json
import os
import datetime
from typing import List, Dict
from pathlib import Path
import shutil


class SiteGenerator:
    def __init__(self, data_dir: str = "data", output_dir: str = "docs", templates_dir: str = "templates"):
        """
        Inicializa el generador de sitio
        
        Args:
            data_dir: Directorio con archivos JSON de noticias
            output_dir: Directorio de salida para el sitio web (docs para GitHub Pages)
            templates_dir: Directorio con templates HTML y CSS
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.templates_dir = Path(templates_dir)
        self.news_data = []
        
    def load_news_data(self) -> bool:
        """
        Carga todos los archivos JSON de noticias disponibles
        
        Returns:
            True si se cargaron datos exitosamente
        """
        try:
            json_files = list(self.data_dir.glob("news_*.json"))
            
            if not json_files:
                print(f"No se encontraron archivos de noticias en {self.data_dir}")
                return False
            
            all_news = []
            for json_file in sorted(json_files, reverse=True):  # Más recientes primero
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_news.extend(data.get('news', []))
                        print(f"Cargadas {len(data.get('news', []))} noticias de {json_file.name}")
                except Exception as e:
                    print(f"Error cargando {json_file}: {e}")
                    continue
            
            self.news_data = all_news
            print(f"Total de noticias cargadas: {len(self.news_data)}")
            return len(self.news_data) > 0
            
        except Exception as e:
            print(f"Error cargando datos de noticias: {e}")
            return False
    
    def load_template(self, template_name: str) -> str:
        """
        Carga un template desde el directorio de templates
        
        Args:
            template_name: Nombre del archivo template
            
        Returns:
            Contenido del template como string
        """
        template_path = self.templates_dir / template_name
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error cargando template {template_name}: {e}")
            return ""
    
    def generate_news_card(self, news: Dict, index: int) -> str:
        """
        Genera una card de noticia usando el template
        
        Args:
            news: Datos de la noticia
            index: Índice de la noticia
            
        Returns:
            HTML de la card generada
        """
        template = self.load_template("news_card.html")
        if not template:
            return ""
        
        # Limpiar la descripción
        description = news.get('description', '')
        if not description:
            # Si no hay descripción, usar el contenido limpio como fallback
            content_preview = news.get('content', '').replace('**', '').replace('*', '')
            content_preview = content_preview.replace('[', '').replace(']', '')
            description = ' '.join(content_preview.split()[:25])  # Primeras 25 palabras
        
        if len(description) > 180:
            description = description[:180] + "..."
        
        # Generar HTML condicionales
        thumbnail_html = ""
        thumbnail = news.get('thumbnail', '')
        if thumbnail:
            thumbnail_html = f'''
                <div class="news-card-image">
                    <img src="{thumbnail}" alt="{news.get('title', 'Noticia')}" loading="lazy">
                </div>
                '''
        
        time = news.get('time', '')
        time_html = f'<div class="news-time">{time}</div>' if time else ''
        time_meta = f' • <strong>Hora:</strong> {time}' if time else ''
        
        description_html = f'<div class="news-description"><p>{description}</p></div>' if description else ''
        
        # Reemplazar placeholders
        replacements = {
            '{{THUMBNAIL_HTML}}': thumbnail_html,
            '{{NEWS_ID}}': str(index + 1),
            '{{CATEGORY}}': news.get('category', 'General'),
            '{{TIME_HTML}}': time_html,
            '{{LINK}}': news.get('link', '#'),
            '{{TITLE}}': news.get('title', 'Sin título'),
            '{{DESCRIPTION_HTML}}': description_html,
            '{{DATE}}': news.get('date', 'N/A'),
            '{{TIME_META}}': time_meta
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def generate_html(self) -> str:
        """
        Genera el HTML principal del sitio usando templates
        
        Returns:
            Contenido HTML completo
        """
        template = self.load_template("index.html")
        if not template:
            return ""
        
        today = datetime.date.today()
        formatted_date = today.strftime("%d de %B de %Y")
        
        # Estadísticas
        total_news = len(self.news_data)
        total_categories = len(set(news.get('category', 'General') for news in self.news_data))
        
        # Generar cards de noticias
        news_cards = ""
        for i, news in enumerate(self.news_data[:50]):  # Limitar a 50 noticias más recientes
            news_cards += self.generate_news_card(news, i)
        
        # Reemplazar placeholders en el template principal
        replacements = {
            '{{TITLE}}': 'Diario Digital - Noticias del Perú',
            '{{DESCRIPTION}}': 'Noticias diarias extraídas automáticamente del Diario Correo',
            '{{LAST_UPDATE}}': f'Última actualización: {formatted_date}',
            '{{TOTAL_NEWS}}': str(total_news),
            '{{TOTAL_CATEGORIES}}': str(total_categories),
            '{{NEWS_CARDS}}': news_cards,
            '{{CURRENT_YEAR}}': str(today.year)
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def create_output_directory(self):
        """Crea el directorio de salida y copia archivos necesarios"""
        self.output_dir.mkdir(exist_ok=True)
        
        # Copiar CSS desde templates
        css_source = self.templates_dir / "styles.css"
        css_dest = self.output_dir / "styles.css"
        
        if css_source.exists():
            shutil.copy2(css_source, css_dest)
            print(f"CSS copiado: {css_dest}")
        else:
            print(f"⚠️ Archivo CSS no encontrado en {css_source}")
        
        print(f"Directorio de salida creado: {self.output_dir}")
    
    def generate_site(self) -> bool:
        """
        Genera el sitio web completo
        
        Returns:
            True si se generó exitosamente
        """
        try:
            # Cargar datos
            if not self.load_news_data():
                return False
            
            # Crear directorio de salida
            self.create_output_directory()
            
            # Generar HTML principal
            html_content = self.generate_html()
            
            # Guardar archivo HTML
            with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Sitio web generado exitosamente en {self.output_dir}")
            print(f"Archivo principal: {self.output_dir}/index.html")
            
            return True
            
        except Exception as e:
            print(f"Error generando el sitio web: {e}")
            return False


def main():
    """Función principal"""
    generator = SiteGenerator()
    
    if generator.generate_site():
        print("¡Sitio web generado exitosamente!")
        return 0
    else:
        print("Error generando el sitio web.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())