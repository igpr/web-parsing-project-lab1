# app.py - ПОЛНЫЙ КОД
"""
Веб-приложение для курсового проекта - интеграционная база данных смартфонов
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Настройки базы данных
DATABASE = 'database/parsing_project.db'

# Создаем фильтр для форматирования дат
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d.%m.%Y'):
    """Форматирует дату для отображения в шаблонах"""
    if value is None:
        return ""
    try:
        # Если это строка, пытаемся распарсить
        if isinstance(value, str):
            # Пробуем разные форматы дат
            for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format)
                except ValueError:
                    continue
            return value
        # Если это datetime объект
        elif isinstance(value, datetime):
            return value.strftime(format)
        else:
            return str(value)
    except:
        return str(value)

# Добавляем текущее время во все шаблоны
@app.context_processor
def inject_now():
    return {'current_time': datetime.now()}

def get_db_connection():
    """Создает подключение к базе данных SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Возвращает строки как словари
    return conn

def init_database():
    """Инициализация базы данных при первом запуске"""
    if not os.path.exists(DATABASE):
        print("База данных не найдена. Создайте ее сначала.")
        return False
    return True

@app.route('/')
def index():
    """Главная страница с поиском"""
    # Получаем топ товаров для отображения
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем случайные товары для главной страницы
    cursor.execute('''
        SELECT p.*, MIN(o.price) as min_price
        FROM products p
        JOIN offers o ON p.id = o.product_id
        GROUP BY p.id
        ORDER BY RANDOM()
        LIMIT 6
    ''')
    featured_products = cursor.fetchall()
    
    # Получаем статистику
    cursor.execute('SELECT COUNT(*) as count FROM products')
    products_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM offers')
    offers_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(DISTINCT website_name) as count FROM offers')
    websites_count = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template('index.html',
                         featured_products=featured_products,
                         products_count=products_count,
                         offers_count=offers_count,
                         websites_count=websites_count)

@app.route('/search')
def search():
    """Страница поиска товаров"""
    query = request.args.get('q', '')
    brand = request.args.get('brand', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Базовый запрос
    sql = '''
        SELECT 
            p.id,
            p.canonical_name,
            p.brand,
            p.model,
            COUNT(o.id) as offers_count,
            MIN(o.price) as min_price,
            MAX(o.price) as max_price,
            ROUND(AVG(o.price), 2) as avg_price
        FROM products p
        JOIN offers o ON p.id = o.product_id
        WHERE 1=1
    '''
    
    params = []
    
    # Добавляем условия поиска
    if query:
        sql += " AND (p.canonical_name LIKE ? OR p.brand LIKE ? OR p.model LIKE ?)"
        params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
    
    if brand:
        sql += " AND p.brand = ?"
        params.append(brand)
    
    if min_price:
        sql += " AND o.price >= ?"
        params.append(float(min_price))
    
    if max_price:
        sql += " AND o.price <= ?"
        params.append(float(max_price))
    
    sql += '''
        GROUP BY p.id
        ORDER BY min_price ASC
        LIMIT 50
    '''
    
    cursor.execute(sql, params)
    search_results = cursor.fetchall()
    
    # Получаем список всех брендов для фильтра
    cursor.execute('SELECT DISTINCT brand FROM products ORDER BY brand')
    brands = [row['brand'] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('search.html',
                         search_results=search_results,
                         query=query,
                         brands=brands,
                         selected_brand=brand,
                         min_price=min_price,
                         max_price=max_price)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Страница детальной информации о товаре"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем информацию о товаре
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    
    if not product:
        conn.close()
        return "Товар не найден", 404
    
    # Получаем все предложения для этого товара
    cursor.execute('''
        SELECT * FROM offers 
        WHERE product_id = ? 
        ORDER BY price ASC
    ''', (product_id,))
    offers = cursor.fetchall()
    
    # Получаем характеристики товара
    cursor.execute('SELECT * FROM attributes WHERE product_id = ?', (product_id,))
    attributes = cursor.fetchall()
    
    # Получаем статистику по ценам
    if offers:
        prices = [offer['price'] for offer in offers]
        price_stats = {
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices),
            'count': len(prices)
        }
    else:
        price_stats = None
    
    conn.close()
    
    return render_template('product.html',
                         product=product,
                         offers=offers,
                         attributes=attributes,
                         price_stats=price_stats)

@app.route('/api/products')
def api_products():
    """API для получения списка товаров (JSON)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            p.id,
            p.canonical_name,
            p.brand,
            p.model,
            COUNT(o.id) as offers_count,
            MIN(o.price) as min_price
        FROM products p
        LEFT JOIN offers o ON p.id = o.product_id
        GROUP BY p.id
        ORDER BY p.canonical_name
        LIMIT 100
    ''')
    
    products = cursor.fetchall()
    conn.close()
    
    # Конвертируем в список словарей
    result = []
    for product in products:
        result.append(dict(product))
    
    return jsonify(result)

@app.route('/api/search')
def api_search():
    """API для поиска товаров"""
    query = request.args.get('q', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            p.id,
            p.canonical_name,
            p.brand,
            MIN(o.price) as min_price
        FROM products p
        JOIN offers o ON p.id = o.product_id
        WHERE p.canonical_name LIKE ? OR p.brand LIKE ?
        GROUP BY p.id
        ORDER BY min_price ASC
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%'))
    
    results = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in results])

@app.route('/stats')
def stats():
    """Страница со статистикой"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Общая статистика
    cursor.execute('SELECT COUNT(*) as count FROM products')
    products_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM offers')
    offers_count = cursor.fetchone()['count']
    
    # Статистика по брендам
    cursor.execute('''
        SELECT 
            p.brand,
            COUNT(DISTINCT p.id) as products_count,
            COUNT(o.id) as offers_count,
            ROUND(MIN(o.price), 2) as min_price,
            ROUND(MAX(o.price), 2) as max_price,
            ROUND(AVG(o.price), 2) as avg_price
        FROM products p
        JOIN offers o ON p.id = o.product_id
        GROUP BY p.brand
        ORDER BY products_count DESC
    ''')
    brand_stats = cursor.fetchall()
    
    # Статистика по сайтам
    cursor.execute('''
        SELECT 
            website_name,
            COUNT(*) as offers_count,
            ROUND(MIN(price), 2) as min_price,
            ROUND(MAX(price), 2) as max_price,
            ROUND(AVG(price), 2) as avg_price
        FROM offers
        GROUP BY website_name
        ORDER BY offers_count DESC
    ''')
    website_stats = cursor.fetchall()
    
    # Последние обновления
    cursor.execute('''
        SELECT website_name, COUNT(*) as count, MAX(date_parsed) as last_parsed
        FROM offers
        GROUP BY website_name
        ORDER BY last_parsed DESC
    ''')
    last_updates = cursor.fetchall()
    
    conn.close()
    
    return render_template('stats.html',
                         products_count=products_count,
                         offers_count=offers_count,
                         brand_stats=brand_stats,
                         website_stats=website_stats,
                         last_updates=last_updates)

@app.route('/about')
def about():
    """Страница о проекте"""
    return render_template('about.html')

if __name__ == '__main__':
    if init_database():
        print("="*60)
        print("ВЕБ-ПРИЛОЖЕНИЕ ДЛЯ КУРСОВОГО ПРОЕКТА")
        print("="*60)
        print(f"База данных: {DATABASE}")
        print("Сервер запускается на http://localhost:5000")
        print("Для остановки нажмите Ctrl+C")
        print("="*60)
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Ошибка инициализации базы данных")