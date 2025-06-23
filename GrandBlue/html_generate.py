import os
import re
from pathlib import Path

# Настройки
IMAGE_FOLDER = 'downloaded_images'  # Папка с изображениями
OUTPUT_FOLDER = 'chapters'         # Папка для HTML-файлов
MANGA_TITLE = 'Grand Blue'         # Название манги

# Создаем папку для глав, если ее нет
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Функция для извлечения информации из имени файла
def parse_filename(filename):
    match = re.match(r'grand_blue_vol(\d+)_ch(\d+\.?\d*)_p(\d+)\.(jpg|png|jpeg)', filename.lower())
    if match:
        return {
            'volume': match.group(1),
            'chapter': match.group(2),
            'page': match.group(3),
            'ext': match.group(4)
        }
    return None

# Собираем все изображения и группируем по главам
chapters = {}
for filename in os.listdir(IMAGE_FOLDER):
    info = parse_filename(filename)
    if info:
        chapter_key = f"vol{info['volume']}_ch{info['chapter']}"
        if chapter_key not in chapters:
            chapters[chapter_key] = []
        chapters[chapter_key].append((int(info['page']), filename))

# Сортируем главы и страницы внутри глав
sorted_chapters = sorted(chapters.items(), key=lambda x: float(x[0].split('_ch')[1]))
for chapter in sorted_chapters:
    chapter[1].sort(key=lambda x: x[0])

# HTML шаблон
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
        <a href="index.html" class="home-button">НА ГЛАВНУЮ</a>
    </div>
</body>
</html>
"""

# Создаем список всех глав для навигации
all_chapters = []
for chapter_key, _ in sorted_chapters:
    chapter_num = chapter_key.split('_ch')[1]
    all_chapters.append((chapter_num, chapter_key))

# Генерируем HTML для каждой главы
for chapter_key, pages in sorted_chapters:
    chapter_num = chapter_key.split('_ch')[1]
    safe_chapter_num = chapter_num.replace('.', '_')
    
    # Генерируем HTML для страниц
    pages_html = []
    for page_num, filename in pages:
        # Используем относительный путь к изображению
        img_path = os.path.join('..', IMAGE_FOLDER, filename).replace('\\', '/')
        pages_html.append(
            f'<div class="page-container">\n'
            f'    <img class="page-image" src="{img_path}" loading="lazy">\n'
            f'</div>'
        )
    
    # Создаем опции для выбора глав
    chapters_options = []
    for ch_num, ch_key in all_chapters:
        safe_ch_num = ch_num.replace('.', '_')
        selected = 'selected' if ch_num == chapter_num else ''
        chapters_options.append(
            f'<option value="chapter_{safe_ch_num}.html" {selected}>Глава {ch_num}</option>'
        )
    
    # Заполняем шаблон
    html_content = HTML_TEMPLATE.format(
        manga_title=MANGA_TITLE,
        chapter_num=chapter_num,
        pages_html='\n'.join(pages_html),
        chapters_options='\n'.join(chapters_options)
    )
    
    # Сохраняем HTML файл
    output_filename = f"chapter_{safe_chapter_num}.html"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Создана глава: {output_path}")

print("\nГенерация глав завершена!")