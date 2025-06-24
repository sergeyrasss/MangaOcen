import os
import re
from pathlib import Path

# Настройки
MANGA_TITLE = 'Grand Blue'
SORTED_MANGA_DIR = '/home/den/MangaOcen/GrandBlue/sorted_manga'
OUTPUT_FOLDER = '/home/den/MangaOcen/GrandBlue/chapters'
MAIN_PAGE_PATH = '/home/den/MangaOcen/index.html'

# Рассчитываем относительный путь
relative_main_path = os.path.relpath(MAIN_PAGE_PATH, OUTPUT_FOLDER)
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

# HTML шаблон с максимальной совместимостью
HTML_TEMPLATE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>{manga_title} - Глава {chapter_num}</title>
    <style type="text/css">
        body {{
            margin: 0;
            padding: 0;
            background-color: #000000;
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
        .navigation {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #000000;
            padding: 10px;
            text-align: center;
            z-index: 100;
        }}
        select {{
            width: 90%;
            max-width: 300px;
            height: 40px;
            margin: 5px auto;
            font-size: 16px;
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #666666;
            -webkit-appearance: menulist;
        }}
        a.button {{
            display: inline-block;
            width: 90%;
            max-width: 300px;
            height: 40px;
            line-height: 40px;
            margin: 5px auto;
            font-size: 16px;
            background-color: #FF6B00;
            color: #FFFFFF;
            text-decoration: none;
            font-weight: bold;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    {pages_html}
    
    <div class="navigation">
        <form action="#" method="get">
            <select name="chapter" onchange="window.location=this.options[this.selectedIndex].value">
                <option value="">Выберите главу...</option>
                {chapters_options}
            </select>
        </form>
        <a href="{relative_main_path}" class="button">НА ГЛАВНУЮ</a>
    </div>
</body>
</html>
"""

# Генерируем HTML файлы
for idx, (chapter_num, chapter_dir, pages) in enumerate(chapters):
    safe_chapter_num = chapter_num.replace('.', '_')
    output_filename = f"chapter_{safe_chapter_num}.html"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    # Генерируем HTML страниц
    pages_html = []
    for page_num, filename in pages:
        img_path = os.path.join('..', 'sorted_manga', chapter_dir, filename).replace('\\', '/')
        pages_html.append(
            '<div class="page-container">'
            f'<img class="page-image" src="{img_path}" alt="Страница {page_num}" />'
            '</div>'
        )
    
    # Опции для выбора глав
    chapters_options = []
    for ch_num, _, _ in chapters:
        safe_num = ch_num.replace('.', '_')
        selected = 'selected="selected"' if ch_num == chapter_num else ''
        chapters_options.append(
            f'<option value="chapter_{safe_num}.html" {selected}>Глава {ch_num}</option>'
        )
    
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
