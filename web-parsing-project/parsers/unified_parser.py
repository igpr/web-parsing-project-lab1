# parsers/unified_parser.py
"""
Универсальный парсер для курсового проекта
Собирает данные из разных источников + генерирует тестовые данные
"""
import json
import os
from datetime import datetime
import random
from faker import Faker

def generate_test_data(count=100, site_name="TestSite"):
    """Генерирует тестовые данные для курсового проекта"""
    fake = Faker('ru_RU')
    Faker.seed(42)
    
    brands = ['Apple', 'Samsung', 'Xiaomi', 'Honor', 'Realme', 'Google', 'OnePlus', 'Nokia']
    models = {
        'Apple': ['iPhone 15 Pro', 'iPhone 15', 'iPhone 14 Pro', 'iPhone 14', 'iPhone 13'],
        'Samsung': ['Galaxy S24 Ultra', 'Galaxy S24+', 'Galaxy S24', 'Galaxy A54', 'Galaxy Z Flip5'],
        'Xiaomi': ['Redmi Note 13 Pro', 'Redmi 12', 'Xiaomi 13T', 'Xiaomi 13 Lite', 'Poco X6 Pro'],
        'Honor': ['Honor 90', 'Honor X8', 'Honor Magic5 Lite', 'Honor 70'],
        'Realme': ['Realme GT 5', 'Realme 11 Pro+', 'Realme C55', 'Realme Narzo 60'],
    }
    
    products = []
    
    for i in range(count):
        brand = random.choice(brands)
        model = random.choice(models.get(brand, ['Unknown Model']))
        
        # Генерируем реалистичные данные
        name = f"Смартфон {brand} {model} {random.choice(['128GB', '256GB', '512GB'])}"
        
        # Цена в зависимости от бренда
        base_prices = {
            'Apple': 70000,
            'Samsung': 50000,
            'Xiaomi': 30000,
            'Honor': 25000,
            'Realme': 20000,
            'Google': 60000,
            'OnePlus': 40000,
            'Nokia': 15000,
        }
        
        price = base_prices.get(brand, 30000) + random.randint(-5000, 10000)
        price_str = f"{price:,} руб.".replace(',', ' ')
        
        product = {
            'id': f"{site_name.lower()}_{i}",
            'name': name,
            'price': price_str,
            'url': f"https://{site_name.lower()}.ru/product/{i}",
            'website': site_name,
            'brand': brand,
            'model': model,
            'memory': random.choice(['128GB', '256GB', '512GB']),
            'color': random.choice(['черный', 'белый', 'синий', 'зеленый', 'фиолетовый']),
            'rating': round(random.uniform(3.5, 5.0), 1),
            'reviews': random.randint(5, 500),
            'parsed_at': datetime.now().isoformat(),
            'is_test_data': True
        }
        
        products.append(product)
    
    return products

def save_to_json(data, filename):
    """Сохраняет данные в JSON файл"""
    os.makedirs('raw_data', exist_ok=True)
    filepath = os.path.join('raw_data', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"   📁 Сохранено в: {filepath}")
    return filepath

def main():
    print("\n" + "="*60)
    print("УНИВЕРСАЛЬНЫЙ ПАРСЕР ДЛЯ КУРСОВОГО ПРОЕКТА")
    print("="*60)
    
    print("\nГенерируем тестовые данные для 3 сайтов...")
    
    # Сайт 1: "Citilink" (тестовые данные)
    print("\n1. Сайт 'Citilink' (тестовые данные):")
    citilink_data = generate_test_data(50, "Citilink")
    save_to_json(citilink_data, "citilink_test.json")
    print(f"   Сгенерировано товаров: {len(citilink_data)}")
    
    # Сайт 2: "DNS-Shop" (тестовые данные)
    print("\n2. Сайт 'DNS-Shop' (тестовые данные):")
    dns_data = generate_test_data(50, "DNS-Shop")
    save_to_json(dns_data, "dns_test.json")
    print(f"   Сгенерировано товаров: {len(dns_data)}")
    
    # Сайт 3: "MVideo" (тестовые данные)
    print("\n3. Сайт 'MVideo' (тестовые данные):")
    mvideo_data = generate_test_data(50, "MVideo")
    save_to_json(mvideo_data, "mvideo_test.json")
    print(f"   Сгенерировано товаров: {len(mvideo_data)}")
    
    # Объединяем все данные
    print("\n4. Объединяем все данные...")
    all_data = citilink_data + dns_data + mvideo_data
    
    save_to_json(all_data, "all_products.json")
    
    print(f"\n✅ ВСЕГО СОБРАНО: {len(all_data)} товаров")
    
    # Статистика
    print("\n📊 СТАТИСТИКА:")
    brands = {}
    for product in all_data:
        brand = product['brand']
        brands[brand] = brands.get(brand, 0) + 1
    
    for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
        print(f"   {brand}: {count} товаров")
    
    print(f"\n📁 Все файлы сохранены в папке 'raw_data/'")
    print("   Теперь можно переходить к созданию базы данных!")

if __name__ == "__main__":
    # Установите faker если нет: pip install faker
    try:
        from faker import Faker
        main()
    except ImportError:
        print("Установите библиотеку faker: pip install faker")