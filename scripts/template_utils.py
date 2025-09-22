#!/usr/bin/env python3
from pathlib import Path

def list_templates():
    templates_dir = Path("templates")
    if not templates_dir.exists():
        return print("❌ Directorio templates/ no encontrado")
    print("📄 Templates disponibles:")
    print("\n".join(f"   • {f.name} ({f.stat().st_size} bytes)" 
          for f in sorted(templates_dir.glob("*")) if f.is_file()))

def validate_templates():
    required = ["index.html", "news_card.html", "styles.css"]
    missing = [f for f in required if not (Path("templates") / f).exists()]
    print("❌ Templates faltantes: " + ", ".join(missing) if missing 
          else "✅ Todos los templates están presentes")
    return not missing

def show_placeholders():
    placeholders = {
        "📄 index.html": ["{{TITLE}}", "{{DESCRIPTION}}", "{{LAST_UPDATE}}", 
                         "{{TOTAL_NEWS}}", "{{TOTAL_CATEGORIES}}", "{{NEWS_CARDS}}", 
                         "{{CURRENT_YEAR}}"],
        "📰 news_card.html": ["{{THUMBNAIL_HTML}}", "{{NEWS_ID}}", "{{CATEGORY}}", 
                             "{{TIME_HTML}}", "{{LINK}}", "{{TITLE}}", 
                             "{{DESCRIPTION_HTML}}", "{{DATE}}", "{{TIME_META}}"]
    }
    print("🔤 Placeholders disponibles:")
    for template, items in placeholders.items():
        print(f"\n{template}:")
        print("\n".join(f"   • {item}" for item in items))

def main():
    commands = {
        "list": list_templates,
        "validate": validate_templates,
        "placeholders": show_placeholders
    }
    import sys
    if len(sys.argv) < 2:
        print("🛠️ Utilidades de Templates - News Scraper\n\nComandos disponibles:")
        print("\n".join(f"  python template_utils.py {cmd} - {func.__doc__ or ''}" 
              for cmd, func in commands.items()))
        return
    
    commands.get(sys.argv[1].lower(), 
                lambda: print(f"❌ Comando desconocido: {sys.argv[1]}"))()

if __name__ == "__main__":
    main()
