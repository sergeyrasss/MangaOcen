import os
import subprocess
from pathlib import Path

def git_operations_for_directory(repo_root, target_dir, start_from_file=None):
    try:
        # Переходим в корень репозитория
        os.chdir(repo_root)
        print(f"📁 Корень репозитория: {os.getcwd()}")

        # Получаем относительный путь к целевой директории
        relative_target = os.path.relpath(target_dir, repo_root)
        
        # Получаем список файлов в целевой директории
        files = sorted([
            f for f in os.listdir(target_dir)
            if os.path.isfile(os.path.join(target_dir, f)) and not f.startswith('.')
        ])
        
        if not files:
            print("ℹ️ Нет файлов для добавления.")
            return
        
        # Определяем начальный индекс
        start_index = 0
        if start_from_file:
            try:
                start_index = files.index(os.path.basename(start_from_file))
                print(f"🔹 Начинаем с файла: {files[start_index]}")
            except ValueError:
                print(f"⚠️ Файл '{start_from_file}' не найден. Начинаем с первого.")

        for file in files[start_index:]:
            file_path = os.path.join(relative_target, file)
            print(f"\n🔹 Обработка файла: {file_path}")

            # 1. git add
            try:
                subprocess.run(["git", "add","-f", file_path], check=True)
                print("✅ Файл добавлен в индекс")
            except subprocess.CalledProcessError:
                print("❌ Ошибка при добавлении файла, пропускаем")
                continue

            # 2. git commit
            try:
                commit_msg = f"Add {file}"
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                print("✅ Коммит создан")
            except subprocess.CalledProcessError:
                print("ℹ️ Файл не изменился или уже добавлен, пропускаем")
                continue

            # 3. git push
            try:
                subprocess.run(["git", "push", "origin", "main"], check=True)
                print("🚀 Изменения отправлены")
            except subprocess.CalledProcessError:
                print("❌ Ошибка при отправке, прерываем выполнение")
                break

    except Exception as e:
        print(f"⚠️ Критическая ошибка: {e}")
    finally:
        print("\n✅ Выполнение завершено")

if __name__ == "__main__":
    # Настройки
    REPO_ROOT = "/home/den/MangaOcen"  # Корень репозитория (где находится .git)
    TARGET_DIR = "/home/den/MangaOcen/GrandBlue/downloaded_images"  # Директория с файлами
    START_FROM_FILE = "grand_blue_vol06_ch024_p007.png"  # Имя файла для старта
    
    git_operations_for_directory(REPO_ROOT, TARGET_DIR, START_FROM_FILE)