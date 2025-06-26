import os
from pathlib import Path

# Конфигурация
MANGA_TITLE = "The Shiunji Family Children"
BASE_DIR = "/home/den/MangaOcen/TheShiunjiFamilyChildren"
OUTPUT_DIR = os.path.join(BASE_DIR, "html_chapters")
CHAPTER_PREFIX = "Chapter"

# Создаем выходную директорию, если ее нет
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_chapter_number(chapter_dir):
    """Извлекаем номер главы из имени директории"""
    return int(chapter_dir.replace(CHAPTER_PREFIX, ""))

def get_sorted_chapters():
    """Получаем отсортированный список глав"""
    chapters = []
    for item in os.listdir(BASE_DIR):
        if item.startswith(CHAPTER_PREFIX):
            chapters.append(item)
    return sorted(chapters, key=get_chapter_number)

def generate_html_for_chapter(chapter_dir, chapters_list):
    """Генерируем HTML для одной главы"""
    chapter_path = os.path.join(BASE_DIR, chapter_dir)
    chapter_num = get_chapter_number(chapter_dir)
    
    # Получаем список страниц и сортируем их
    pages = []
    for item in os.listdir(chapter_path):
        if item.lower().endswith('.png'):
            pages.append(item)
    
    # Сортируем страницы по номеру
    pages.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    
    # Генерируем HTML
    html = f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{MANGA_TITLE} - {chapter_dir}</title>
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
            border-radius: 4px;
        }}
        a.button {{
            display: block;
            width: 100%;
            height: 40px;
            line-height: 40px;
            font-size: 16px;
            background-color: #FF6B00;
            color: #FFF;
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            border-radius: 20px;
            border: none;
        }}
    </style>
</head>
<body>
'''
    # Добавляем страницы
    for page in pages:
        html += f'    <div class="page-container"><img class="page-image" src="../{chapter_dir}/{page}" alt="{page}" /></div>\n'

    # Добавляем навигационную панель
    html += f'''
    <div class="nav-container">
        <div class="nav-inner">
            <select onchange="window.location.href=this.value;">
                <option value="">Выберите главу...</option>
'''
    
    # Добавляем опции для выбора главы
    for chapter in chapters_list:
        c_num = get_chapter_number(chapter)
        selected = ' selected="selected"' if c_num == chapter_num else ''
        html += f'                <option value="chapter_{c_num}.html"{selected}>{chapter}</option>\n'
    
    html += '''
            </select>
            <a href="../../index.html" class="button">НА ГЛАВНУЮ</a>
        </div>
    </div>
</body>
</html>
'''
    
    # Сохраняем HTML файл
    output_file = os.path.join(OUTPUT_DIR, f"chapter_{chapter_num}.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_file

def main():
    chapters = get_sorted_chapters()
    print(f"Найдено глав: {len(chapters)}")
    
    for chapter in chapters:
        output_file = generate_html_for_chapter(chapter, chapters)
        print(f"Сгенерирован: {output_file}")
    
    print("Генерация завершена!")

if __name__ == "__main__":
    main()