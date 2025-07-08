import os
from pathlib import Path

# Конфигурация
MANGA_TITLE = "A Couple of Cuckoo's"
CHAPTERS_DIR = "/home/den/MangaOcen/ACoupleofCuckoo's"
OUTPUT_DIR = "/home/den/MangaOcen/ACoupleofCuckoo's/html"
TEMPLATE_FILE = "template.html"

# Создаем директорию для HTML-файлов
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Получаем и сортируем список глав
chapters = sorted(
    [d for d in os.listdir(CHAPTERS_DIR) if d.startswith("Chapter")],
    key=lambda x: float(x[7:].replace("_", ".")) if x[7:].replace("_", "").isdigit() else 0
)

# Генерируем HTML для выпадающего списка
options_html = []
for chapter in chapters:
    chapter_num = chapter[7:]
    display_num = chapter_num.replace("_", ".")
    option_value = f"chapter_{chapter_num.lower().replace('_', '.')}.html"
    options_html.append(f'<option value="{option_value}">Глава {display_num}</option>')

options_html = "\n".join(options_html)

# Функция создания HTML-файла для главы
def create_chapter_html(chapter_dir, chapter_num):
    # Получаем и сортируем страницы
    pages = sorted(
        [f for f in os.listdir(os.path.join(CHAPTERS_DIR, chapter_dir)) 
         if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
        key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)
    )
    
    # Генерируем HTML для страниц
    pages_html = []
    for page in pages:
        img_path = f"../{chapter_dir}/{page}"
        alt_text = f"Страница {''.join(filter(str.isdigit, page))}"
        pages_html.append(f'<div class="page-container"><img class="page-image" src="{img_path}" alt="{alt_text}" /></div>')
    
    pages_html = "\n".join(pages_html)
    
    # Читаем шаблон и заменяем плейсхолдеры
    with open(TEMPLATE_FILE, 'r') as f:
        template = f.read()
    
    html = template.replace("<!-- PAGES_PLACEHOLDER -->", pages_html)
    html = html.replace("<!-- OPTIONS_PLACEHOLDER -->", options_html)
    
    # Устанавливаем selected для текущей главы
    current_chapter_value = f"chapter_{chapter_num.lower().replace('_', '.')}.html"
    html = html.replace(f'value="{current_chapter_value}"', f'value="{current_chapter_value}" selected="selected"')
    
    # Сохраняем HTML-файл
    output_filename = os.path.join(OUTPUT_DIR, f"chapter_{chapter_num.lower().replace('_', '.')}.html")
    with open(output_filename, 'w') as f:
        f.write(html)

# Создаем шаблон, если его нет
if not os.path.exists(TEMPLATE_FILE):
    with open(TEMPLATE_FILE, 'w') as f:
        f.write(f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{MANGA_TITLE} - Глава CHAPTER_NUM</title>
    <style type="text/css">
        body {{
            margin: 0;
            padding: 0;
            background-color: #000;
            -webkit-text-size-adjust: none;
        }}
        .page-container {{
            width: 100%;
            text-align: center;
            margin: 0 auto;
            padding: 0;
        }}
        .page-image {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        .nav-container {{
            width: 100%;
            background-color: #000;
            padding: 15px 10px;
            text-align: center;
            border-top: 1px solid #333;
        }}
        .nav-inner {{
            max-width: 500px;
            margin: 0 auto;
        }}
        select {{
            width: 100%;
            height: 40px;
            margin-bottom: 10px;
            font-size: 16px;
            background-color: #333;
            color: #FFF;
            border: 1px solid #666;
            -webkit-appearance: menulist;
            border-radius: 20px;
            padding: 0 15px;
        }}
        a.button {{
            display: block;
            width: 100%;
            height: 40px;
            line-height: 40px;
            font-size: 16px;
            background: #00b4db; /* Голубой цвет */
            color: #FFF;
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            border: none;
            border-radius: 20px;
            box-shadow: 0 3px 5px rgba(0,0,0,0.3);
            text-shadow: 0 1px 1px rgba(0,0,0,0.3);
            -webkit-tap-highlight-color: transparent;
        }}
        a.button:active {{
            background: #0083b0; /* Темнее при нажатии */
        }}
    </style>
</head>
<body>
    <!-- PAGES_PLACEHOLDER -->
    <div class="nav-container">
        <div class="nav-inner">
            <select onchange="window.location.href=this.value;">
                <option value="">Выберите главу...</option>
                <!-- OPTIONS_PLACEHOLDER -->
            </select>
            <a href="/MangaOcen/index.html" class="button">НА ГЛАВНУЮ</a>
        </div>
    </div>
</body>
</html>""")

# Генерируем HTML для всех глав
for chapter in chapters:
    chapter_num = chapter[7:]
    create_chapter_html(chapter, chapter_num)

print(f"Создано {len(chapters)} HTML-файлов в {OUTPUT_DIR}")