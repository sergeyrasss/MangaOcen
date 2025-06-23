import os
import subprocess
from pathlib import Path

# Настройки
REPO_ROOT = "/home/den/MangaOcen"
CHAPTERS_DIR = os.path.join(REPO_ROOT, "GrandBlue", "sorted_chapters")

# Переходим в корень репозитория
os.chdir(REPO_ROOT)

# Получаем отсортированный список глав (с поддержкой дробных номеров)
chapters = sorted(
    [d for d in os.listdir(CHAPTERS_DIR) if d.startswith("Chapter_")],
    key=lambda x: float(x.split("_")[1])
)

for chapter in chapters:
    chapter_path = os.path.join("GrandBlue", "sorted_chapters", chapter)
    
    # Добавляем только эту папку главы
    subprocess.run(["git", "add", chapter_path])
    
    # Проверяем, есть ли изменения для коммита
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if chapter_path in status.stdout:
        subprocess.run(["git", "commit", "-m", f"Добавлена {chapter}"])
        subprocess.run(["git", "push", "origin", "main"])
        print(f"Успешно: {chapter} добавлена и отправлена!")
    else:
        print(f"Нет изменений в {chapter}, пропускаем")

print("\nВсе главы обработаны!")