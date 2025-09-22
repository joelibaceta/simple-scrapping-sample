#!/usr/bin/env python3
import sys, subprocess, os
from pathlib import Path

def run_command(command, desc=""):
    print(f"🔄 {desc}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout if result.stdout else "")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}\n{e.stderr if e.stderr else ''}")
        return False

def main():
    os.chdir(Path(__file__).parent)
    
    steps = [
        ("python scraper.py", "📰 Ejecutando scraper..."),
        ("python site_generator.py", "🎨 Generando sitio web...")
    ]
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            return 1
    
    if not all(Path(f).exists() for f in ["docs/index.html", "docs/styles.css"]):
        print("❌ Archivos necesarios no encontrados")
        return 1
    
    news_count = len(list(Path("data").glob("news_*.json")))
    print(f"\n🎉 Despliegue exitoso!\n📊 {news_count} archivos de noticias procesados")
    print("\n🌐 Para ver: cd docs && python -m http.server 8000")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
