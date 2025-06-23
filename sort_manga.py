import os
import shutil
from pathlib import Path

# Путь к папке с изображениями
source_dir = Path("/home/den/MangaOcen/GrandBlue/downloaded_images")

# Проверяем, существует ли исходная папка
if not source_dir.exists():
    print(f"Ошибка: Папка {source_dir} не найдена!")
    exit(1)

# Создаём папку для отсортированных глав (если её нет)
output_dir = source_dir.parent / "sorted_chapters"
output_dir.mkdir(exist_ok=True)

# Проходим по всем файлам в исходной папке
for file_path in source_dir.glob("grand_blue_*.jpg"):
    # Разбираем имя файла (пример: grand_blue_vol01_ch001_p003.jpg)
    parts = file_path.stem.split("_")
    
    # Получаем номер главы (ch001 → 001)
    chapter_num = parts[3][2:]  # Убираем 'ch'
    
    # Создаём папку для главы (если её нет)
    chapter_dir = output_dir / f"Chapter_{chapter_num}"
    chapter_dir.mkdir(exist_ok=True)
    
    # Копируем файл в нужную папку
    shutil.copy2(file_path, chapter_dir)
    print(f"Файл {file_path.name} перемещён в {chapter_dir}")

print("Сортировка завершена!")