import os
import re
from pathlib import Path

# Настройки
MANGA_TITLE = 'Grand Blue'
SORTED_MANGA_DIR = '/home/den/MangaOcen/GrandBlue/sorted_manga'
OUTPUT_FOLDER = '/home/den/MangaOcen/GrandBlue/chapters'
MAIN_PAGE_PATH = '/home/den/MangaOcen/index.html'  # Абсолютный путь к главной странице

# Рассчитываем относительный путь от папки chapters до главной страницы
relative_main_path = os.path.relpath(MAIN_PAGE_PATH, OUTPUT_FOLDER)

# Создаем папку для глав
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def parse_chapter_number(chapter_dir):
    match = re.match(r'Chapter (\d+\.?\d*)', chapter_dir)
    return match.group(1) if match else None

# Собираем и сортируем главы
chapters = []
for chapter_dir in sorted(os.listdir(SORTED_MANGA_DIR), key=lambda x: float(parse_chapter_number(x) or 0)):
    chapter_num = parse_chapter_number(chapter_dir)
    if not chapter_num:
        continue
    
    chapter_path = os.path.join(SORTED_MANGA_DIR, chapter_dir)
    if not os.path.isdir(chapter_path):
        continue
    
    pages = []
    for filename in sorted(os.listdir(chapter_path)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            page_match = re.search(r'_p(\d+)\.', filename.lower())
            if page_match:
                pages.append((int(page_match.group(1)), filename))
    
    if pages:
        chapters.append((chapter_num, chapter_dir, sorted(pages, key=lambda x: x[0])))

# HTML шаблон с обновленной ссылкой
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{manga_title} - Глава {chapter_num}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background-color: #000;
            overflow-x: hidden;
        }}
        .page-container {{
            width: 100vw;
            margin: 0;
            padding: 0;
        }}
        .page-image {{
            width: 100%;
            display: block;
            margin: 0 auto;
        }}
        .chapter-navigation {{
            background-color: #000;
            padding: 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }}
        .chapter-selector {{
            padding: 12px 25px;
            border-radius: 25px;
            border: none;
            background-color: #222;
            color: white;
            font-size: 18px;
            width: 90%;
            max-width: 400px;
            cursor: pointer;
        }}
        .home-button {{
            padding: 12px 25px;
            border-radius: 25px;
            border: none;
            background-color: #FF6B00;
            color: white;
            font-size: 18px;
            width: 90%;
            max-width: 400px;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
        }}
        @media (orientation: landscape) {{
            .page-image {{
                width: auto;
                height: 100vh;
            }}
        }}
    </style>
</head>
<body>
    <div class="reader-content">
        {pages_html}
    </div>
    
    <div class="chapter-navigation">
        <select class="chapter-selector" onchange="location = this.value;">
            <option value="">Выберите главу...</option>
            {chapters_options}
        </select>
        <a href="{relative_main_path}" class="home-button">НА ГЛАВНУЮ</a>
    </div>
</body>
</html>
"""

# Генерируем HTML файлы
for chapter_num, chapter_dir, pages in chapters:
    safe_chapter_num = chapter_num.replace('.', '_')
    output_filename = f"chapter_{safe_chapter_num}.html"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    # Генерируем HTML страниц
    pages_html = []
    for page_num, filename in pages:
        img_path = os.path.join('..', 'sorted_manga', chapter_dir, filename).replace('\\', '/')
        pages_html.append(
            f'<div class="page-container">\n'
            f'    <img class="page-image" src="{img_path}" loading="lazy">\n'
            f'</div>'
        )
    
    # Опции для выбора глав
    chapters_options = [
        f'<option value="chapter_{ch_num.replace(".", "_")}.html" '
        f'{"selected" if ch_num == chapter_num else ""}>'
        f'Глава {ch_num}</option>'
        for ch_num, _, _ in chapters
    ]
    
    # Заполняем шаблон
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE.format(
            manga_title=MANGA_TITLE,
            chapter_num=chapter_num,
            pages_html='\n'.join(pages_html),
            chapters_options='\n'.join(chapters_options),
            relative_main_path=relative_main_path
        ))
    
    print(f"Создана глава: {output_path}")

print(f"\nГенерация завершена! Главная страница: {MAIN_PAGE_PATH}")
