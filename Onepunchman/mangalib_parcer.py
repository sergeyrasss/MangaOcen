import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """Настройка драйвера Chrome с обходом защиты"""
    chrome_options = Options()
    
    # Основные настройки
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Обход защиты от ботов
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(20)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Ошибка при запуске браузера: {e}")
        return None

def extract_chapter_info(url):
    """Извлекаем номер главы из URL в формате ChapterX(или ChapterX.Y)"""
    parts = url.split('/')
    for part in parts:
        if part.startswith('c') and any(char.isdigit() for char in part):
            # Уберем "c" и получим часть после нее
            chapter_part = part[1:]
            # Проходим по символам, оставляем цифры и максимум одну точку
            chapter_num = ''
            dot_found = False
            for ch in chapter_part:
                if ch.isdigit():
                    chapter_num += ch
                elif ch == '.' and not dot_found:
                    chapter_num += ch
                    dot_found = True
                else:
                    break  # прекращаем, если встречаем что-то другое
            if chapter_num:
                return f"Chapter{chapter_num}"
    return "Chapter1"  # Значение по умолчанию
		
def find_manga_image(driver):
    """Усовершенствованный поиск изображения манги"""
    try:
        # Основной метод через reader-view-img
        try:
            img = WebDriverWait(driver, 7).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.reader-view-img"))
            )
            src = img.get_attribute("src") or img.get_attribute("data-src")
            if src and "manga" in src:
                return src
        except:
            pass

        # Альтернативный метод через reader-container
        try:
            container = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".reader-container"))
            )
            bg_image = container.value_of_css_property("background-image")
            if bg_image and "url(" in bg_image:
                url = bg_image.split("url(")[1].split(")")[0].strip('"\'')
                if "manga" in url:
                    return url
        except:
            pass

        # Экстренный метод через JavaScript
        try:
            js_script = """
            var target = document.querySelector('img[src*="/manga/"]') || 
                         document.querySelector('img[data-src*="/manga/"]');
            if (target) return target.src || target.getAttribute('data-src');
            
            var divs = document.querySelectorAll('div[style*="background-image"]');
            for (var i = 0; i < divs.length; i++) {
                var bg = divs[i].style.backgroundImage;
                if (bg && bg.includes('/manga/')) {
                    return bg.match(/url\\(['"]?(.*?)['"]?\\)/)[1];
                }
            }
            return null;
            """
            result = driver.execute_script(js_script)
            if result:
                return result
        except:
            pass

        return None
    except Exception as e:
        print(f"Ошибка при поиске изображения: {e}")
        return None

def download_image(img_url, referer, save_path):
    """Надежное скачивание изображения"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": referer,
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        }
        
        with requests.get(img_url, headers=headers, stream=True, timeout=15) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return False

def navigate_next(driver):
    """Переход к следующей странице с проверкой"""
    try:
        # Прокрутка и нажатие стрелки
        driver.execute_script("window.scrollBy(0, 200)")
        body = driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.ARROW_RIGHT)
        time.sleep(1.5)  # Оптимальное время ожидания
        return True
    except Exception as e:
        print(f"Ошибка навигации: {e}")
        return False

def get_page_number(url):
    """Извлекаем номер страницы из URL"""
    if 'p=' in url:
        return url.split('p=')[1].split('&')[0]
    return "1"

def main():
    start_url = "https://mangalib.me/ru/706--onepunchman/read/v28/c180?bid&p=1"
    max_attempts = 3  # Максимальное количество попыток при одинаковом URL
    
    driver = setup_driver()
    if not driver:
        return
    
    try:
        # Инициализация переменных
        current_url = start_url
        prev_url = ""
        same_url_count = 0
        
        while True:
            print(f"\nОбработка: {current_url}")
            
            # Обновляем имя папки для текущей главы
            chapter_name = extract_chapter_info(current_url)
            os.makedirs(chapter_name, exist_ok=True)
            
            # Проверка изменения URL
            if current_url == prev_url:
                same_url_count += 1
                if same_url_count >= max_attempts:
                    print("URL не изменяется, завершение работы")
                    break
            else:
                same_url_count = 0
                prev_url = current_url
            
            # Загрузка страницы
            driver.get(current_url)
            time.sleep(1.5)  # Оптимальное время ожидания
            
            # Поиск изображения
            img_url = find_manga_image(driver)
            if img_url:
                page_num = get_page_number(current_url)
                save_path = f"{chapter_name}/Page{page_num}.jpg"
                
                if download_image(img_url, current_url, save_path):
                    print(f"Успешно сохранено: {save_path}")
                else:
                    print("Пропуск из-за ошибки загрузки")
            else:
                print("Изображение не найдено (продолжаем)")
            
            # Переход к следующей странице
            if not navigate_next(driver):
                same_url_count += 1
                if same_url_count >= max_attempts:
                    break
                continue
                
            # Проверка изменения URL
            new_url = driver.current_url
            if new_url == current_url:
                print("URL не изменился после перехода")
                same_url_count += 1
            else:
                current_url = new_url
            
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        driver.quit()
        print("\nРабота завершена")

if __name__ == "__main__":
    main()