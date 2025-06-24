import os
import subprocess
import time
from pathlib import Path

# Настройки
REPO_ROOT = "/home/den/MangaOcen"
IMAGES_DIR = os.path.join(REPO_ROOT, "GrandBlue", "downloaded_images")
BATCH_SIZE = 30  # Количество файлов в одном коммите
DELAY = 10  # Задержка между операциями в секундах

def run_command(cmd):
    """Выполняет команду с обработкой ошибок"""
    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def process_batch(batch_files, batch_num):
    """Обрабатывает пакет файлов"""
    print(f"\nОбработка пакета {batch_num} ({len(batch_files)} файлов)")
    
    # Добавляем файлы
    added_count = 0
    for file in batch_files:
        success, output = run_command(["git", "add", file])
        if success:
            added_count += 1
        else:
            print(f"Ошибка добавления {file}: {output}")
    
    if added_count == 0:
        return False
    
    # Коммит
    commit_msg = f"Добавлено {added_count} изображений (пакет {batch_num})"
    success, output = run_command(["git", "commit", "-m", commit_msg])
    if not success:
        print(f"Ошибка коммита: {output}")
        run_command(["git", "reset"])
        return False
    
    # Push
    for attempt in range(3):
        success, output = run_command(["git", "push", "origin", "main"])
        if success:
            return True
        print(f"Ошибка push (попытка {attempt+1}): {output}")
        if attempt < 2:
            print(f"Повтор через {DELAY} сек...")
            time.sleep(DELAY)
    return False

def main():
    os.chdir(REPO_ROOT)
    
    # Получаем список всех изображений
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        image_files.extend([
            os.path.join("GrandBlue", "downloaded_images", f) 
            for f in os.listdir(IMAGES_DIR) 
            if f.lower().endswith(ext)
        ])
    
    if not image_files:
        print("Не найдено изображений для обработки!")
        return
    
    image_files.sort()
    print(f"Найдено {len(image_files)} изображений")
    
    # Разбиваем на пакеты
    batches = [image_files[i:i+BATCH_SIZE] for i in range(0, len(image_files), BATCH_SIZE)]
    
    # Обрабатываем каждый пакет
    success_count = 0
    for i, batch in enumerate(batches, 1):
        if process_batch(batch, i):
            success_count += 1
        time.sleep(DELAY)
    
    print(f"\nУспешно обработано пакетов: {success_count}/{len(batches)}")
    print(f"Всего изображений: {len(image_files)}")

if __name__ == "__main__":
    main()