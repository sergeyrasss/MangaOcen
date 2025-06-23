import os
import requests
from datetime import datetime
import time
import subprocess
import atexit

# Настройки
DOWNLOAD_FOLDER = 'downloaded_images'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Функция для запрета сна системы
def inhibit_sleep():
    try:
        # Создаем inhibitor через systemd
        cmd = [
            'systemd-inhibit',
            '--what=idle:sleep:shutdown',
            '--who=DesuCityDownloader',
            '--why=Downloading_images',
            '--mode=block',
            'python3', os.path.abspath(__file__)
        ]
        # Если запускаем основной скрипт, просто возвращаем None
        if os.environ.get('INHIBIT_RUN'):
            return None
        # Иначе запускаем себя через inhibitor
        os.environ['INHIBIT_RUN'] = '1'
        subprocess.run(cmd)
        exit()
    except Exception as e:
        print(f"⚠️ Не удалось запретить спящий режим: {e}")

# Вызываем при старте
inhibit_sleep()

# Функция для восстановления нормального режима сна
def restore_sleep():
    print("\n🔄 Восстанавливаем нормальный режим сна системы...")

# Регистрируем восстановление при выходе
atexit.register(restore_sleep)

# Чтение ссылок
with open('grand_blue_images.txt', 'r') as f:
    image_urls = [line.strip() for line in f if line.strip()]

# Заголовки для обхода защиты
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Referer': 'https://desu.city/',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
}

success_count = 0
fail_count = 0
failed_urls = []

print(f"🚀 Начало загрузки {len(image_urls)} изображений...")

for i, url in enumerate(image_urls, 1):
    try:
        filename = os.path.join(DOWNLOAD_FOLDER, os.path.basename(url))
        
        if os.path.exists(filename):
            print(f"⏩ [{i}/{len(image_urls)}] Уже существует: {filename}")
            success_count += 1
            continue
            
        print(f"⬇️ [{i}/{len(image_urls)}] Загрузка: {url}")
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        
        success_count += 1
        print(f"✅ Успешно сохранено: {filename}")
        time.sleep(1)
        
    except requests.exceptions.RequestException as e:
        fail_count += 1
        failed_urls.append(url)
        print(f"❌ Ошибка при загрузке: {str(e)}")
    except Exception as e:
        fail_count += 1
        failed_urls.append(url)
        print(f"⚠️ Неожиданная ошибка: {str(e)}")

print(f"\n📊 Итоги: Успешно - {success_count}, Ошибок - {fail_count}")

if failed_urls:
    print("\nСсылки которые не удалось загрузить:")
    for url in failed_urls:
        print(f"- {url}")