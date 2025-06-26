import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin

def parse_images_from_html(html):
    """Парсит HTML и извлекает список изображений из Reader.init"""
    try:
        pattern = r'Reader\.init\(({.*?})\);'
        match = re.search(pattern, html, re.DOTALL)
        
        if not match:
            return None
        
        init_block = match.group(1)
        images_pattern = r'images:\s*(\[\[.*?\]\])'
        images_match = re.search(images_pattern, init_block, re.DOTALL)
        
        if not images_match:
            return None
        
        images_str = images_match.group(1)
        
        try:
            images_str = images_str.replace("'", '"')
            return json.loads(images_str)
        except json.JSONDecodeError:
            try:
                import ast
                return ast.literal_eval(images_str)
            except (SyntaxError, ValueError):
                return None
    except Exception as e:
        print(f"Ошибка при парсинге HTML: {str(e)[:100]}")
        return None

def get_chapter_images(chapter_url):
    """Получает список изображений для конкретной главы"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(chapter_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        images = parse_images_from_html(response.text)
        if not images:
            return None
        
        base_match = re.search(r'dir:\s*"([^"]+)"', response.text)
        if not base_match:
            base_url = "https://img4.desu.city/manga/rus/grand_blue/"
        else:
            base_url = base_match.group(1)
            if base_url.startswith('//'):
                base_url = 'https:' + base_url
            elif not base_url.startswith('http'):
                base_url = 'https://img4.desu.city' + base_url
        
        image_urls = []
        for img in images:
            filename = img[0] if isinstance(img, (list, tuple)) and len(img) > 0 else str(img)
            filename = filename.lstrip('/')
            full_url = base_url.rstrip('/') + '/' + filename
            image_urls.append(full_url)
        
        return image_urls
    except Exception as e:
        print(f"Ошибка при обработке главы {chapter_url}: {str(e)[:100]}...")
        return None

def get_chapter_links(main_url):
    """Получает список всех глав с основной страницы"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(main_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        
        chapter_links = []
        base_domain = "https://desu.city"
        
        for a_tag in soup.find_all('a', {'class': 'tips Tooltip'}):
            href = a_tag.get('href')
            if href:
                full_url = urljoin(base_domain, href)
                chapter_links.append(full_url)
        
        chapter_links = sorted(list(set(chapter_links)), reverse=True)
        return chapter_links
    except Exception as e:
        print(f"Ошибка при загрузке главной страницы: {e}")
        return []

def save_to_file(filename, data):
    """Сохраняет данные в текстовый файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(f"{item}\n")

def main():
    main_url = "https://desu.city/manga/grand-blue.825/"
    output_file = "grand_blue_images.txt"
    
    print("Получаем список глав...")
    chapter_links = get_chapter_links(main_url)
    
    if not chapter_links:
        print("Не удалось получить список глав")
        return
    
    print(f"Найдено глав: {len(chapter_links)}")
    
    all_image_urls = []
    
    for i, chapter_url in enumerate(chapter_links, 1):
        print(f"\nГлава {i}/{len(chapter_links)}: {chapter_url}")
        
        image_urls = get_chapter_images(chapter_url)
        if not image_urls:
            print(" ⚠️ Не удалось получить изображения для этой главы")
            continue
        
        print(f" ✅ Найдено изображений: {len(image_urls)}")
        all_image_urls.extend(image_urls)
        
        # Добавляем задержку между запросами
        if i < len(chapter_links):
            time.sleep(2)
    
    # Сохраняем все URL в файл
    save_to_file(output_file, all_image_urls)
    print(f"\nВсего собрано URL изображений: {len(all_image_urls)}")
    print(f"Результаты сохранены в файл: {output_file}")

if __name__ == "__main__":
    main()