import os
import subprocess
from pathlib import Path

def git_commit_chapters(repo_root, sorted_dir, start_from=None):
    """
    Коммитит каждую папку с главой отдельно, начиная с указанной
    Новый формат структуры: Chapter{номер} (без пробела)
    """
    os.chdir(repo_root)
    print(f"📌 Рабочая директория: {os.getcwd()}")

    # Получаем и сортируем список папок с главами
    chapters = sorted(
        [d for d in os.listdir(sorted_dir) if d.startswith("Chapter")],
        key=lambda x: int(x.replace("Chapter", ""))
    )

    if not chapters:
        print("❌ Не найдено папок с главами")
        return

    # Определяем стартовый индекс
    start_index = 0
    if start_from:
        # Нормализуем формат начальной папки (ChapterX или просто X)
        start_from = start_from if start_from.startswith("Chapter") else f"Chapter{start_from}"
        try:
            start_index = chapters.index(start_from)
            print(f"🔹 Начинаем с главы: {start_from}")
        except ValueError:
            print(f"⚠️ Глава '{start_from}' не найдена. Начинаем с первой главы")

    # Обрабатываем главы начиная с указанной
    for chapter in chapters[start_index:]:
        chapter_path = os.path.join(sorted_dir, chapter)
        print(f"\n🔹 Обрабатываю главу: {chapter}")

        # 1. Добавляем файлы главы
        try:
            subprocess.run(["git", "add", f"{chapter_path}/*"], check=True)
            print("✅ Файлы добавлены в индекс")
        except subprocess.CalledProcessError:
            print("⚠️ Нет изменений для добавления")
            continue

        # 2. Создаем коммит
        try:
            commit_msg = f"Add {chapter} files"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            print("💾 Коммит создан")
        except subprocess.CalledProcessError:
            print("⚠️ Нет изменений для коммита")
            continue

        # 3. Отправляем изменения
        try:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("🚀 Изменения отправлены на GitHub")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при отправке: {e}")
            break

if __name__ == "__main__":
    # Конфигурация
    REPO_ROOT = "/home/den/MangaOcen/TheShiunjiFamilyChildren"  # Указывает корневую папку Git-репозитория, куда будут заливаться файлы.
    SORTED_DIR = "/home/den/MangaOcen/TheShiunjiFamilyChildren"  # Папка с главами (должна быть в папке локального репозитория)
    START_FROM = "Chapter1"  # Начать с этой главы (None - с первой)

    # Проверяем существование директорий
    if not os.path.isdir(REPO_ROOT):
        print(f"❌ Директория репозитория не существует: {REPO_ROOT}")
    elif not os.path.isdir(SORTED_DIR):
        print(f"❌ Директория с главами не существует: {SORTED_DIR}")
    else:
        git_commit_chapters(REPO_ROOT, SORTED_DIR, START_FROM)
    print("\n✅ Все главы обработаны!")