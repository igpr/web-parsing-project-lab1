# parsers/dns_selenium.py
"""
Парсер для DNS-Shop на Selenium - ПРОСТОЙ И РАБОЧИЙ ВАРИАНТ
"""
import json
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver(headless=True):
    """Настраивает браузер"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless=new")
    
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    # Отключаем обнаружение Selenium
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Скрываем WebDriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    
    driver.implicitly_wait(10)
    return driver

def parse_dns_with_selenium():
    """Парсим смартфоны с DNS-Shop"""
    print("\n" + "="*60)
    print("ПАРСЕР DNS-SHOP - ПРОСТОЙ И РАБОЧИЙ")
    print("="*60)
    
    # URL категории смартфонов на DNS-Shop
    category_url = "https://www.dns-shop.ru/catalog/17a8a01d16404e77/smartfony/"
    products_to_parse = 10  # Начнем с 10 товаров
    all_products_data = []
    
    # Запускаем видимый браузер для первого теста
    driver = setup_driver(headless=False)
    
    try:
        print(f"\n1. Открываем страницу: {category_url}")
        driver.get(category_url)
        time.sleep(3)  # Ждем загрузки
        
        # Делаем скриншот
        driver.save_screenshot('raw_data/dns_initial.png')
        print("   Скриншот сохранен: raw_data/dns_initial.png")
        
        print("\n2. Прокручиваем страницу...")
        
        # Прокручиваем несколько раз
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {1000 * (i+1)});")
            time.sleep(1.5)
        
        print("\n3. Ищем карточки товаров...")
        
        # DNS-Shop использует такой селектор для карточек товаров
        # Давайте попробуем несколько вариантов
        selectors = [
            "div.catalog-product",  # Основной селектор
            "div.product",  # Альтернативный
            "div.catalog-2-level-product-card",  # Еще вариант
        ]
        
        product_cards = []
        working_selector = ""
        
        for selector in selectors:
            try:
                found = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(found) > 0:
                    product_cards = found
                    working_selector = selector
                    print(f"   ✅ Нашел селектор: '{selector}' - {len(product_cards)} товаров")
                    break
            except:
                continue
        
        if not product_cards:
            print("   ❌ Не нашел товары по стандартным селекторам. Пробую другой метод...")
            
            # Ищем по структуре страницы
            page_html = driver.page_source
            if "Смартфон" in page_html or "iPhone" in page_html:
                print("   ℹ️ Товары есть на странице, попробуем другой подход...")
                
                # Ищем все элементы с классом, содержащим "product"
                all_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='product']")
                print(f"   Найдено элементов с 'product' в классе: {len(all_elements)}")
                
                # Фильтруем только те, что выглядят как карточки товаров
                for elem in all_elements[:30]:  # Проверим первые 30
                    try:
                        text = elem.text
                        if "₽" in text and ("Смартфон" in text or "iPhone" in text or "Samsung" in text):
                            product_cards.append(elem)
                    except:
                        continue
                
                print(f"   Отфильтровал как товары: {len(product_cards)}")
        
        if not product_cards:
            print("\n⚠️ Не удалось найти товары. Возможные причины:")
            print("   1. Блокировка от DNS-Shop")
            print("   2. Изменилась структура сайта")
            print("   3. Нужно больше времени для загрузки")
            
            # Покажем что есть на странице
            body_text = driver.find_element(By.TAG_NAME, 'body').text[:300]
            print(f"\n   Первые 300 символов текста страницы:\n{body_text}")
            return
        
        print(f"\n4. Парсим первые {min(products_to_parse, len(product_cards))} товаров...")
        
        for i, card in enumerate(product_cards[:products_to_parse]):
            try:
                # Прокручиваем к карточке
                driver.execute_script("arguments[0].scrollIntoView(true);", card)
                time.sleep(0.3)
                
                # Получаем HTML карточки
                card_html = card.get_attribute('outerHTML')
                
                # Название
                name = "Неизвестно"
                try:
                    # Пробуем разные селекторы для названия
                    name_selectors = [
                        "a.catalog-product__name",
                        "div.catalog-product__name",
                        "span.catalog-product__name",
                        "h3",
                        "a[href*='/product/']"
                    ]
                    
                    for ns in name_selectors:
                        try:
                            name_elem = card.find_element(By.CSS_SELECTOR, ns)
                            name = name_elem.text.strip()
                            if name and len(name) > 3:
                                break
                        except:
                            continue
                    
                    # Если не нашли через селекторы, попробуем извлечь из текста карточки
                    if name == "Неизвестно":
                        card_text = card.text
                        lines = card_text.split('\n')
                        for line in lines:
                            if "Смартфон" in line or "iPhone" in line or "Xiaomi" in line or "Samsung" in line:
                                name = line.strip()
                                break
                
                except Exception as e:
                    name = f"Ошибка получения названия: {str(e)[:30]}"
                
                # Цена
                price = "Цена не указана"
                try:
                    price_selectors = [
                        "div.product-buy__price",
                        "span.product-buy__price",
                        "div.catalog-product__price",
                        "span.price",
                        "[class*='price']"
                    ]
                    
                    for ps in price_selectors:
                        try:
                            price_elem = card.find_element(By.CSS_SELECTOR, ps)
                            price_text = price_elem.text.strip()
                            if "₽" in price_text and len(price_text) < 20:
                                price = price_text
                                break
                        except:
                            continue
                
                except:
                    pass
                
                # Ссылка
                url = ""
                try:
                    link_elem = card.find_element(By.CSS_SELECTOR, "a")
                    url = link_elem.get_attribute("href")
                except:
                    pass
                
                # Бренд
                brand = "Неизвестно"
                if "Apple" in name or "iPhone" in name:
                    brand = "Apple"
                elif "Samsung" in name:
                    brand = "Samsung"
                elif "Xiaomi" in name:
                    brand = "Xiaomi"
                elif "Realme" in name:
                    brand = "Realme"
                elif "Honor" in name:
                    brand = "Honor"
                
                print(f"   [{i+1}] {name[:40]}... - {price}")
                
                # Сохраняем данные
                product_data = {
                    'id': f"dns_{i}",
                    'name': name,
                    'price': price,
                    'url': url,
                    'website': 'DNS-Shop',
                    'brand': brand,
                    'deduplication_key': f"{brand}_{name}",
                    'parsed_at': datetime.now().isoformat()
                }
                
                all_products_data.append(product_data)
                
            except Exception as e:
                print(f"   ❌ Ошибка с товаром {i+1}: {e}")
                continue
        
        # 5. Сохраняем данные
        if all_products_data:
            print(f"\n5. УСПЕХ! Собрано {len(all_products_data)} товаров")
            
            os.makedirs('raw_data', exist_ok=True)
            filename = f'raw_data/dns_selenium_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_products_data, f, ensure_ascii=False, indent=2)
            
            print(f"   📁 Данные сохранены: {filename}")
            
            # Покажем пример данных
            print("\n   Пример данных:")
            for i, product in enumerate(all_products_data[:2]):
                print(f"   {i+1}. {product['name'][:40]}... - {product['price']}")
        
        else:
            print("\n❌ Не удалось собрать данные")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n6. Завершаю работу...")
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    parse_dns_with_selenium()
    print("\n" + "="*60)
    print("РАБОТА ЗАВЕРШЕНА")
    print("="*60)