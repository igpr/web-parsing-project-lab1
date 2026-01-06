# parsers/citilink_selenium.py
"""
УЛУЧШЕННЫЙ ПАРСЕР ДЛЯ CITILINK С ОТЛАДКОЙ
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

def setup_driver(visible=True):
    """Настраивает браузер. По умолчанию ВИДИМЫЙ для отладки."""
    chrome_options = Options()
    
    # ВАЖНО: ЗАКОММЕНТИРУЕМ headless для отладки!
    # chrome_options.add_argument("--headless=new")
    
    # Дополнительные настройки
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # User-Agent для имитации реального пользователя
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    # Отключаем автоматизационные флаги
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Автоматическая установка драйвера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Убираем опознавание как бота
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    
    driver.implicitly_wait(15)  # Увеличиваем время ожидания
    return driver

def parse_citilink_with_selenium():
    """Основная функция парсинга с улучшенной отладкой"""
    print("\n" + "="*60)
    print("УЛУЧШЕННЫЙ ПАРСЕР CITILINK - РЕЖИМ ОТЛАДКИ")
    print("="*60)
    
    # Конфигурация
    category_url = "https://www.citilink.ru/catalog/smartfony/"
    products_to_parse = 3
    all_products_data = []
    
    driver = setup_driver(visible=True)  # Браузер будет ВИДЕН
    
    try:
        print(f"\n1. Открываем страницу: {category_url}")
        driver.get(category_url)
        
        # Сохраняем скриншот сразу после загрузки
        driver.save_screenshot('raw_data/01_initial_load.png')
        print("   Скриншот начальной загрузки сохранен")
        
        # Ждем загрузки страницы
        print("\n2. Ждем 5 секунд для полной загрузки...")
        time.sleep(5)
        
        # Прокручиваем страницу для подгрузки товаров
        print("\n3. Прокручиваем страницу...")
        
        # Прокрутка вниз
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)
        driver.save_screenshot('raw_data/02_after_first_scroll.png')
        
        driver.execute_script("window.scrollTo(0, 2000);")
        time.sleep(2)
        
        driver.execute_script("window.scrollTo(0, 3000);")
        time.sleep(2)
        driver.save_screenshot('raw_data/03_after_scrolling.png')
        
        # Теперь ищем товары РАЗНЫМИ СПОСОБАМИ
        print("\n4. Ищем товары разными методами...")
        
        # Способ 1: Ищем по классу ProductCardHorizontal
        print("\n   Способ 1: Ищем 'div.ProductCardHorizontal'")
        try:
            cards_method1 = driver.find_elements(By.CSS_SELECTOR, "div.ProductCardHorizontal")
            print(f"   Найдено: {len(cards_method1)} товаров")
        except Exception as e:
            print(f"   Ошибка: {e}")
        
        # Способ 2: Ищем по data-meta-name
        print("\n   Способ 2: Ищем '[data-meta-name=\"ProductCardHorizontal\"]'")
        try:
            cards_method2 = driver.find_elements(By.CSS_SELECTOR, '[data-meta-name="ProductCardHorizontal"]')
            print(f"   Найдено: {len(cards_method2)} товаров")
        except Exception as e:
            print(f"   Ошибка: {e}")
        
        # Способ 3: Ищем по class, содержащему product-card
        print("\n   Способ 3: Ищем '[class*=\"product-card\"]'")
        try:
            cards_method3 = driver.find_elements(By.CSS_SELECTOR, '[class*="product-card"]')
            print(f"   Найдено: {len(cards_method3)} товаров")
        except Exception as e:
            print(f"   Ошибка: {e}")
        
        # Способ 4: Ищем по структуре, которая есть на Citilink
        print("\n   Способ 4: Ищем 'div[data-meta-name]'")
        try:
            cards_method4 = driver.find_elements(By.CSS_SELECTOR, 'div[data-meta-name]')
            print(f"   Найдено элементов с data-meta-name: {len(cards_method4)}")
            
            # Выведем все уникальные data-meta-name для анализа
            meta_names = set()
            for card in cards_method4[:10]:
                meta_name = card.get_attribute("data-meta-name")
                if meta_name:
                    meta_names.add(meta_name)
            print(f"   Уникальные data-meta-name: {list(meta_names)}")
        except Exception as e:
            print(f"   Ошибка: {e}")
        
        # Выберем рабочий метод
        if len(cards_method1) > 0:
            product_cards = cards_method1
            print(f"\n✅ Используем Способ 1. Карточек: {len(product_cards)}")
        elif len(cards_method2) > 0:
            product_cards = cards_method2
            print(f"\n✅ Используем Способ 2. Карточек: {len(product_cards)}")
        else:
            print("\n❌ Не удалось найти товары! Покажем HTML структуру...")
            
            # Сохраняем весь HTML для анализа
            with open('raw_data/debug_full_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source[:10000])  # Первые 10000 символов
            
            # Ищем любой текст на странице
            page_text = driver.find_element(By.TAG_NAME, 'body').text[:500]
            print(f"\nПервые 500 символов текста страницы:\n{page_text}")
            
            return
        
        # 5. Парсим найденные товары
        print(f"\n5. Парсим первые {products_to_parse} товаров...")
        
        for i, card in enumerate(product_cards[:products_to_parse]):
            try:
                print(f"\n   Товар #{i+1}:")
                
                # Прокручиваем к карточке
                driver.execute_script("arguments[0].scrollIntoView(true);", card)
                time.sleep(0.5)
                
                # Название товара
                name = "Не найдено"
                try:
                    name_elem = card.find_element(By.CSS_SELECTOR, "a[data-meta-name='ProductLink']")
                    name = name_elem.text.strip()
                    print(f"     Название: {name[:50]}...")
                except:
                    try:
                        name_elem = card.find_element(By.CSS_SELECTOR, "a.ProductCardHorizontal__title")
                        name = name_elem.text.strip()
                        print(f"     Название: {name[:50]}...")
                    except:
                        print("     Название: не удалось найти")
                
                # Цена
                price = "Цена не указана"
                try:
                    price_elem = card.find_element(By.CSS_SELECTOR, "span.ProductPrice__price")
                    price = price_elem.text.strip()
                    print(f"     Цена: {price}")
                except:
                    try:
                        price_elem = card.find_element(By.CLASS_NAME, "ProductPrice__price")
                        price = price_elem.text.strip()
                        print(f"     Цена: {price}")
                    except:
                        print("     Цена: не найдена")
                
                # Ссылка
                url = ""
                try:
                    link_elem = card.find_element(By.TAG_NAME, "a")
                    url = link_elem.get_attribute("href")
                    print(f"     Ссылка: {url[:80]}...")
                except:
                    print("     Ссылка: не найдена")
                
                # Сохраняем данные
                if name != "Не найдено":
                    product_data = {
                        'id': f"citilink_{i}",
                        'name': name,
                        'price': price,
                        'url': url,
                        'website': 'Citilink',
                        'parsed_at': datetime.now().isoformat()
                    }
                    all_products_data.append(product_data)
                
            except Exception as e:
                print(f"   Ошибка при парсинге товара {i+1}: {e}")
                continue
        
        # 6. Сохраняем данные
        if all_products_data:
            print(f"\n6. Успешно! Собрано {len(all_products_data)} товаров.")
            
            os.makedirs('raw_data', exist_ok=True)
            filename = f'raw_data/citilink_selenium_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_products_data, f, ensure_ascii=False, indent=2)
            
            print(f"   Данные сохранены в: {filename}")
            
            # Показываем первые 2 товара
            print("\n   Первые товары:")
            for i, product in enumerate(all_products_data[:2]):
                print(f"   {i+1}. {product['name'][:40]}... - {product['price']}")
        
        else:
            print("\n⚠️  Не удалось собрать данные ни по одному товару.")
            print("\n   СОВЕТЫ ПО РЕШЕНИЮ:")
            print("   1. Проверьте скриншоты в папке raw_data/")
            print("   2. Возможно, нужна капча или блокировка")
            print("   3. Попробуйте другой сайт (DNS-Shop)")
            print("   4. Проверьте интернет-соединение")
    
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n7. Закрываем браузер через 10 секунд...")
        print("   Посмотрите на открытое окно Chrome!")
        time.sleep(10)
        driver.quit()
        print("   Браузер закрыт.")

if __name__ == "__main__":
    parse_citilink_with_selenium()
    print("\n" + "="*60)
    print("ОТЛАДКА ЗАВЕРШЕНА")
    print("="*60)