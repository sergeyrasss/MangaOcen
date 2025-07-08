import os
import zipfile
import rarfile
import glob

def unpack_cbr_files():
    # Находим все .cbr файлы в текущей директории
    cbr_files = glob.glob('Chapter*.cbr')
    
    for cbr_file in cbr_files:
        try:
            folder_name = os.path.splitext(cbr_file)[0]
            
            # Создаем папку для распаковки
            os.makedirs(folder_name, exist_ok=True)
            success = False
            
            # Сначала пробуем как ZIP архив
            try:
                with zipfile.ZipFile(cbr_file, 'r') as zf:
                    zf.extractall(folder_name)
                print(f"Успешно распакован как ZIP: {cbr_file} -> {folder_name}")
                success = True
            except zipfile.BadZipFile:
                pass
            
            # Если не ZIP, пробуем как RAR архив
            if not success:
                try:
                    with rarfile.RarFile(cbr_file) as rf:
                        rf.extractall(folder_name)
                    print(f"Успешно распакован как RAR: {cbr_file} -> {folder_name}")
                    success = True
                except rarfile.NotRarFile:
                    pass
            
            if success:
                # Удаляем оригинальный архив после успешной распаковки
                os.remove(cbr_file)
                print(f"Удален оригинальный архив: {cbr_file}")
            else:
                print(f"Файл не является ни ZIP, ни RAR архивом: {cbr_file}")
            
        except Exception as e:
            print(f"Ошибка при обработке {cbr_file}: {str(e)}")

if __name__ == "__main__":
    # Проверяем доступность unrar
    if not rarfile.UNRAR_TOOL:
        print("Не найден unrar. Установите его:")
        print("  Ubuntu/Debian: sudo apt install unrar")
        print("  Windows: скачайте с rarlab.com")
        print("  MacOS: brew install unrar")
    
    unpack_cbr_files()
    print("Обработка завершена")