import os
import subprocess

def git_operations_for_directory(directory, start_from_file=None):
    os.chdir(directory)
    
    # Получаем список файлов, исключая скрытые
    files = sorted([f for f in os.listdir() if os.path.isfile(f) and not f.startswith('.')])
    
    if not files:
        print("Нет файлов для добавления.")
        return
    
    # Определяем, с какого файла начать
    if start_from_file:
        try:
            start_index = files.index(start_from_file)
        except ValueError:
            print(f"Файл '{start_from_file}' не найден. Начинаем с первого.")
            start_index = 0
    else:
        start_index = 0
    
    # Обрабатываем файлы начиная с выбранного
    for file in files[start_index:]:
        full_path = os.path.abspath(file)
        
        # Git add
        add_cmd = f"git add \"{full_path}\""
        print(f"> {add_cmd}")
        subprocess.run(add_cmd, shell=True, check=True)
        
        # Git commit
        commit_msg = f"\"Добавлен файл: {full_path}\""
        commit_cmd = f"git commit -m {commit_msg}"
        print(f"> {commit_cmd}")
        subprocess.run(commit_cmd, shell=True, check=True)
        
        # Git push
        push_cmd = "git push origin main"
        print(f"> {push_cmd}")
        subprocess.run(push_cmd, shell=True, check=True)
        
        print(f"Файл '{file}' успешно отправлен.\n")

if __name__ == "__main__":
    # Укажите путь к директории здесь (вместо input)
    TARGET_DIRECTORY = "/home/den/MangaOcen/GrandBlue/downloaded_images"  # ⚠️ Замените на свой путь!
    
    # Укажите файл, с которого начать (или None для начала с первого)
    START_FROM_FILE = "/home/den/MangaOcen/GrandBlue/downloaded_images/grand_blue_vol06_ch022_p025.png"  # Например: "example.txt"
    
    if not os.path.isdir(TARGET_DIRECTORY):
        print("Ошибка: директория не существует!")
    else:
        git_operations_for_directory(TARGET_DIRECTORY, START_FROM_FILE)