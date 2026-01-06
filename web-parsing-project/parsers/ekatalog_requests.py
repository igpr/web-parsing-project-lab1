# parsers/ekatalog_requests.py
"""
Парсер для e-katalog.ru через requests + BeautifulSoup
Самый простой и надежный вариант для курсового проекта
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
import re

def parse_ekatalog():
    """Парсим смартфоны с e-katalog.ru"""
    print("\n" + "="*60)
    print("ПАРСЕР E-KATALOG - ПРОСТОЙ И НАДЕЖНЫЙ")
    print("="*60)
    
    # Базовые настройки
    base_url = "https://www.e-katalog.ru"
    category_url = "https://www.e-katalog.ru/list/122/smartfony/"
    
    # Заголовки для имитации браузера
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    all_products = []
    
    try:
        print(f"\n1. Загружаем страницу: {category_url}")
        
        # Делаем запрос
        response = requests.get(category_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ Ошибка: HTTP {response.status_code}")
            return
        
        print(f"   ✅ Страница загружена ({len(response.text)} символов)")
        
        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n2. Ищем товары на странице...")
        
        # E-Katalog использует такой класс для карточек товаров
        product_blocks = soup.find_all('div', class_='model-short-block')
        
        if not product_blocks:
            # Альтернативный поиск
            product_blocks = soup.find_all('div', class_=re.compile(r'model-short'))
            print(f"   Альтернативный поиск: {len(product_blocks)} товаров")
        else:
            print(f"   Найдено товаров: {len(product_blocks)}")
        
        if not product_blocks:
            print("   ❌ Не найдено товаров. Сохраняю HTML для отладки...")
            with open('raw_data/ekatalog_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("   HTML сохранен: raw_data/ekatalog_debug.html")
            return
        
        print(f"\n3. Парсим первые 15 товаров...")
        
        for i, block in enumerate(product_blocks[:15]):
            try:
                # Название товара
                name_elem = block.find('span', class_='u')
                if not name_elem:
                    name_elem = block.find('a', class_='model-short-title')
                
                name = name_elem.text.strip() if name_elem else "Неизвестно"
                
                # Ссылка на товар
                link_elem = block.find('a', class_='model-short-title')
                if link_elem:
                    product_url = base_url + link_elem['href'] if link_elem.get('href') else ""
                else:
                    product_url = ""
                
                # Цена
                price = "Цена не указана"
                price_elem = block.find('div', class_='model-price-range')
                if price_elem:
                    price = price_elem.text.strip().replace('\n', ' ')
                else:
                    # Ищем цену в других местах
                    price_span = block.find('span', class_='price')
                    if price_span:
                        price = price_span.text.strip()
                
                # Бренд (извлекаем из названия)
                brand = "Неизвестно"
                brand_keywords = [
                    'Apple', 'Samsung', 'Xiaomi', 'Honor', 'Realme', 'Google',
                    'OnePlus', 'Nokia', 'Tecno', 'Infinix', 'OPPO', 'vivo',
                    'POCO', 'Motorola', 'ASUS', 'Huawei', 'Lenovo'
                ]
                
                for keyword in brand_keywords:
                    if keyword.lower() in name.lower():
                        brand = keyword
                        break
                
                # Характеристики (попробуем найти)
                specs = []
                specs_elem = block.find('div', class_='model-short-description')
                if specs_elem:
                    specs_text = specs_elem.text.strip()
                    specs = [s.strip() for s in specs_text.split(',')[:3]]
                
                product_data = {
                    'id': f"ekatalog_{i}",
                    'name': name,
                    'price': price,
                    'url': product_url,
                    'website': 'E-Katalog',
                    'brand': brand,
                    'specs': specs[:3],  # Первые 3 характеристики
                    'deduplication_key': f"{brand}_{name[:50]}",
                    'parsed_at': datetime.now().isoformat()
                }
                
                all_products.append(product_data)
                print(f"   [{i+1}] {name[:40]}... - {price}")
                
                # Пауза между товарами
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ⚠️ Ошибка с товаром {i+1}: {e}")
                continue
        
        # 4. Сохраняем данные
        if all_products:
            print(f"\n4. УСПЕХ! Собрано {len(all_products)} товаров")
            
            os.makedirs('raw_data', exist_ok=True)
            filename = f'raw_data/ekatalog_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_products, f, ensure_ascii=False, indent=2)
            
            print(f"   📁 Данные сохранены: {filename}")
            
            # Показываем пример
            print("\n   Пример данных:")
            for i, product in enumerate(all_products[:3]):
                print(f"   {i+1}. {product['name'][:35]}...")
                print(f"      Цена: {product['price']}")
                print(f"      Бренд: {product['brand']}")
                print()
        
        else:
            print("\n❌ Не удалось собрать данные")
    
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

def parse_multiple_pages():
    """Парсим несколько страниц для сбора 100+ товаров"""
    print("\n" + "="*60)
    print("ПАРСИНГ НЕСКОЛЬКИХ СТРАНИЦ E-KATALOG")
    print("="*60)
    
    base_url = "https://www.e-katalog.ru"
    all_products = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    # Парсим первые 3 страницы (это около 100 товаров)
    for page in range(1, 4):
        print(f"\n📄 Страница {page}...")
        
        if page == 1:
            url = "https://www.e-katalog.ru/list/122/smartfony/"
        else:
            url = f"https://www.e-katalog.ru/list/122/smartfony/{page}/"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"   ❌ Ошибка загрузки страницы {page}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем товары
            product_blocks = soup.find_all('div', class_='model-short-block')
            
            for block in product_blocks:
                try:
                    # Название
                    name_elem = block.find('span', class_='u') or block.find('a', class_='model-short-title')
                    name = name_elem.text.strip() if name_elem else "Неизвестно"
                    
                    # Цена
                    price = "Цена не указана"
                    price_elem = block.find('div', class_='model-price-range') or block.find('span', class_='price')
                    if price_elem:
                        price = price_elem.text.strip().replace('\n', ' ')
                    
                    # Бренд
                    brand = "Неизвестно"
                    for keyword in ['Apple', 'Samsung', 'Xiaomi', 'Honor', 'Realme', 'Google']:
                        if keyword.lower() in name.lower():
                            brand = keyword
                            break
                    
                    product_data = {
                        'id': f"ekatalog_{len(all_products)}",
                        'name': name,
                        'price': price,
                        'website': 'E-Katalog',
                        'brand': brand,
                        'page': page
                    }
                    
                    all_products.append(product_data)
                    
                except:
                    continue
            
            print(f"   ✅ Собрано: {len(product_blocks)} товаров (всего: {len(all_products)})")
            
            # Пауза между страницами
            time.sleep(2)
            
        except Exception as e:
            print(f"   ⚠️ Ошибка на странице {page}: {e}")
            continue
    
    # Сохраняем все товары
    if all_products:
        filename = f'raw_data/ekatalog_full_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Всего собрано: {len(all_products)} товаров")
        print(f"📁 Сохранено в: {filename}")
        
        # Статистика по брендам
        print("\n📊 Статистика по брендам:")
        brands = {}
        for product in all_products:
            brand = product['brand']
            brands[brand] = brands.get(brand, 0) + 1
        
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
            print(f"   {brand}: {count} товаров")

if __name__ == "__main__":
    print("\nВыберите режим:")
    print("1. Тестовый парсинг (15 товаров)")
    print("2. Полный парсинг (100+ товаров)")
    
    choice = input("\nВведите 1 или 2: ").strip()
    
    if choice == "2":
        parse_multiple_pages()
    else:
        parse_ekatalog()
    
    print("\n" + "="*60)
    print("РАБОТА ЗАВЕРШЕНА")
    print("="*60)