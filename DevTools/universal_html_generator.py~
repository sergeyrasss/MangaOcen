import os
from pathlib import Path

# ====================== КОНФИГУРАЦИЯ ======================
MANGA_TITLE = "The Shiunji Family Children"
BASE_DIR = "/home/den/MangaOcen/TheShiunjiFamilyChildren"
OUTPUT_DIR = os.path.join(BASE_DIR, "html_chapters")
CHAPTER_PREFIX = "Chapter"

# ====================== КОНЕЦ КОНФИГУРАЦИИ ======================

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_chapter_number(chapter_dir):
    """Извлекаем номер главы из имени директории"""
    # Более надёжный способ извлечения чисел
    numbers = ''.join(filter(str.isdigit, chapter_dir))
    return int(numbers) if numbers else 0

def extract_page_number(filename):
    """Извлекаем номер страницы из имени файла"""
    # Ищем последовательности цифр в имени файла
    numbers = ''.join(filter(str.isdigit, os.path.splitext(filename)[0]))
    return int(numbers) if numbers else 0

def get_sorted_chapters():
    """Получаем отсортированный список глав"""
    chapters = []
    for item in os.listdir(BASE_DIR):
        if item.startswith(CHAPTER_PREFIX):
            try:
                # Проверяем, что можем извлечь номер главы
                get_chapter_number(item)
                chapters.append(item)
            except ValueError:
                continue
    return sorted(chapters, key=get_chapter_number)

def generate_html_for_chapter(chapter_dir, chapters_list):
    """Генерируем HTML для одной главы"""
    chapter_path = os.path.join(BASE_DIR, chapter_dir)
    chapter_num = get_chapter_number(chapter_dir)
    
    # Получаем и сортируем страницы
    pages = []
    for item in os.listdir(chapter_path):
        if item.lower().endswith(('.png', '.jpg', '.jpeg')):
            pages.append(item)
    
    try:
        # Сортируем страницы по извлечённому номеру
        pages.sort(key=extract_page_number)
    except ValueError as e:
        print(f"Ошибка сортировки страниц в главе {chapter_dir}: {e}")
        # Если не удалось отсортировать, используем порядок файловой системы
        pages.sort()
    
    # Остальной код генерации HTML без изменений
    html = f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" />
    <title>{MANGA_TITLE} - {chapter_dir}</title>
    <style type="text/css">
        body {{
            margin: 0;
            padding: 0;
            background-color: #000;
            -webkit-text-size-adjust: none;
            overflow-x: hidden;
            width: 100%;
        }}
        .page-container {{
            width: 100%;
            margin: 0 auto;
            padding: 0;
            overflow: hidden;
            display: block;
        }}
        .page-image {{
            width: 100%;
            height: auto;
            display: block;
            margin: 0;
            padding: 0;
            border: none;
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
        html += f'<div class="page-container"><img class="page-image" src="../{chapter_dir}/{page}" alt="" /></div>\n'

    # Навигационная панель
    html += f'''
    <div class="nav-container">
        <div class="nav-inner">
            <select onchange="window.location.href=this.value;">
                <option value="">Выберите главу...</option>
'''
    
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
    
    output_file = os.path.join(OUTPUT_DIR, f"chapter_{chapter_num}.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_file

def main():
    chapters = get_sorted_chapters()
    print(f"Найдено глав: {len(chapters)}")
    
    for chapter in chapters:
        try:
            output_file = generate_html_for_chapter(chapter, chapters)
            print(f"Сгенерирован: {output_file}")
        except Exception as e:
            print(f"Ошибка при обработке главы {chapter}: {e}")
    
    print("Генерация завершена!")

if __name__ == "__main__":
    main()