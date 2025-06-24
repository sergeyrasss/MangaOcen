import os
import subprocess
from pathlib import Path

def git_operations_for_directory(directory, start_from_file=None):
    try:
        # Сохраняем исходную директорию для возврата
        original_dir = os.getcwd()
        
        # Проверяем и переходим в целевую директорию
        if not os.path.isdir(directory):
            print(f"❌ Директория не существует: {directory}")
            return
        
        os.chdir(directory)
        print(f"📁 Рабочая директория: {os.getcwd()}")

        # Получаем список файлов
        files = sorted([
            f for f in os.listdir() 
            if os.path.isfile(f) and not f.startswith('.')
        ])
        
        if not files:
            print("ℹ️ Нет файлов для добавления.")
            return
        
        # Определяем начальный индекс
        start_index = 0
        if start_from_file:
            # Извлекаем только имя файла из пути, если передан полный путь
            start_file_name = os.path.basename(start_from_file)
            try:
                start_index = files.index(start_file_name)
                print(f"🔹 Начинаем с файла: {start_file_name}")
            except ValueError:
                print(f"⚠️ Файл '{start_file_name}' не найден. Начинаем с первого.")

        for file in files[start_index:]:
            print(f"\n🔹 Обработка файла: {file}")

            # 1. git add (используем относительный путь)
            try:
                subprocess.run(["git", "add", file], check=True)
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

    finally:
        # Всегда возвращаемся в исходную директорию
        os.chdir(original_dir)

if __name__ == "__main__":
    # Настройки
    TARGET_DIRECTORY = "/home/den/MangaOcen/GrandBlue/downloaded_images"
    START_FROM_FILE = "grand_blue_vol06_ch022_p025.png"  # Только имя файла
    
    git_operations_for_directory(TARGET_DIRECTORY, START_FROM_FILE)