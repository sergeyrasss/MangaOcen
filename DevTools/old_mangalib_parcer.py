import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from PIL import Image
import time
import sys

def get_chapter_and_page(url):
    """Извлекает номер главы и страницы из URL"""
    chapter_match = re.search(r'/c(\d+)\?', url)
    page_match = re.search(r'p=(\d+)', url)
    
    if not chapter_match:
        return None, None
        
    chapter_num = chapter_match.group(1)
    page_num = page_match.group(1) if page_match else "1"
    return chapter_num, page_num

def process_chapter(driver, start_url, max_pages=1000):
    """Обрабатывает все страницы главы, возвращает URL следующей главы (если есть)"""
    chapter_num, current_page = get_chapter_and_page(start_url)
    
    if chapter_num is None:
        return None  # Прекращаем обработку, если не удалось определить главу
        
    chapter_folder = f"Chapter{chapter_num}"
    os.makedirs(chapter_folder, exist_ok=True)
    
    processed_pages = 0
    current_url = start_url
    
    while processed_pages < max_pages:
        output_file = os.path.join(chapter_folder, f"Page{current_page}.png")
        
        if os.path.exists(output_file):
            print(f"Файл {output_file} уже существует. Пропускаем...")
        else:
            print(f"Обработка: {chapter_folder}, Страница {current_page}")
            driver.get(current_url)
            time.sleep(2)
            
            # Скриншот и обрезка
            temp_file = "temp_screen.png"
            driver.save_screenshot(temp_file)
            img = Image.open(temp_file)
            cropped_img = img.crop((1520, 90, img.width - 1529, img.height - 830))
            cropped_img.save(output_file)
            os.remove(temp_file)
            print(f"Сохранено: {output_file}")
        
        processed_pages += 1
        
        # Пытаемся перейти на следующую страницу
        body = driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.ARROW_RIGHT)
        time.sleep(1)
        
        new_url = driver.current_url
        new_chapter, new_page = get_chapter_and_page(new_url)
        
        # Если не удалось определить главу, прекращаем обработку
        if new_chapter is None:
            return None
            
        # Если URL не изменился, значит, мы дошли до конца главы
        if new_url == current_url:
            print(f"Глава {chapter_num} завершена.")
            break
        
        # Если глава изменилась, возвращаем URL следующей главы
        if new_chapter != chapter_num:
            print(f"Обнаружен переход к главе {new_chapter}.")
            return new_url
        
        current_url, current_page = new_url, new_page
    
    return None  # Следующая глава не найдена

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=3840,2160")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        current_url = "https://mangalib.me/ru/12803--isekai-ojisan/read/v1/c1?p=1"
        
        while current_url:
            print(f"\nНачинаем обработку главы: {current_url}")
            next_chapter_url = process_chapter(driver, current_url)
            
            if next_chapter_url is None:
                # Проверяем, была ли ошибка определения главы
                chapter_num, _ = get_chapter_and_page(current_url)
                if chapter_num is None:
                    print("Ошибка: не удалось определить номер главы. Завершение работы.")
                    break
                else:
                    print("Больше глав не найдено. Завершение...")
                    break
                    
            current_url = next_chapter_url
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    finally:
        driver.quit()
        print("Все операции завершены. Браузер закрыт.")

if __name__ == "__main__":
    main()