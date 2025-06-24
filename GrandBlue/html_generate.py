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

# HTML шаблон с оптимизациями
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            touch-action: pan-y;
        }}
        .page-container {{
            width: 100vw;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
        }}
        .page-image {{
            max-width: 100%;
            max-height: 100vh;
            object-fit: contain;
            display: block;
        }}
        .chapter-navigation {{
            background-color: #000;
            padding: 15px;
            text-align: center;
            position: fixed;
            bottom: 0;
            width: 100%;
            z-index: 100;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }}
        .chapter-selector {{
            padding: 10px 20px;
            border-radius: 20px;
            border: none;
            background-color: #222;
            color: white;
            font-size: 16px;
            width: 100%;
            max-width: 350px;
            cursor: pointer;
        }}
        .home-button {{
            padding: 10px 20px;
            border-radius: 20px;
            border: none;
            background-color: #FF6B00;
            color: white;
            font-size: 16px;
            width: 100%;
            max-width: 350px;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
        }}
        @media (min-width: 768px) {{
            .page-image {{
                max-width: 80%;
            }}
        }}
    </style>
</head>
<body>
    {pages_html}
    
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
for idx, (chapter_num, chapter_dir, pages) in enumerate(chapters):
    safe_chapter_num = chapter_num.replace('.', '_')
    output_filename = f"chapter_{safe_chapter_num}.html"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    # Генерируем HTML страниц с предзагрузкой
    pages_html = []
    for i, (page_num, filename) in enumerate(pages):
        img_path = os.path.join('..', 'sorted_manga', chapter_dir, filename).replace('\\', '/')
        
        # Добавляем предзагрузку для следующего изображения
        preload = ""
        if i < len(pages) - 1:
            next_img = os.path.join('..', 'sorted_manga', chapter_dir, pages[i+1][1]).replace('\\', '/')
            preload = f'<link rel="preload" as="image" href="{next_img}">'
        
        pages_html.append(f"""
            {preload}
            <div class="page-container">
                <img class="page-image" src="{img_path}" loading="eager" 
                     alt="Страница {page_num}" decoding="async">
            </div>
        """)
    
    # Опции для выбора глав
    chapters_options = []
    for ch_num, _, _ in chapters:
        safe_num = ch_num.replace('.', '_')
        selected = 'selected' if ch_num == chapter_num else ''
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
