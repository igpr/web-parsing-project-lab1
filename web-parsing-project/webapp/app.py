import sys
import os

# Добавляем корневую папку проекта в путь Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from database.models import db, Product, Offer, ProductAttribute

app = Flask(__name__)

# SQLite база данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/search')
def search():
    """API поиска товаров"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    try:
        # Если есть поисковый запрос
        if query:
            results = Product.query.filter(
                (Product.canonical_name.ilike(f'%{query}%')) |
                (Product.description.ilike(f'%{query}%')) |
                (Product.brand.ilike(f'%{query}%'))
            ).paginate(page=page, per_page=per_page, error_out=False)
        else:
            # Все товары
            results = Product.query.order_by(Product.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        
        # Формируем ответ
        products_data = []
        for product in results.items:
            # Находим минимальную цену
            min_price = None
            offers_count = 0
            
            if product.offers:
                prices = [offer.price for offer in product.offers if offer.price is not None]
                if prices:
                    min_price = min(prices)
                offers_count = len(product.offers)
            
            products_data.append({
                'id': product.id,
                'name': product.canonical_name,
                'brand': product.brand,
                'description': (product.description or "")[:100] + "..." if product.description and len(product.description) > 100 else (product.description or ""),
                'min_price': min_price,
                'offers_count': offers_count,
                'image_url': product.image_url or 'https://via.placeholder.com/300?text=No+Image'
            })
        
        return jsonify({
            'success': True,
            'products': products_data,
            'total': results.total,
            'pages': results.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/product/<int:product_id>')
def product_detail(product_id):
    """Информация о товаре"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Все предложения
        offers = []
        for offer in product.offers:
            offers.append({
                'id': offer.id,
                'website': offer.website_name,
                'price': offer.price,
                'url': offer.url,
                'in_stock': offer.in_stock,
                'date_parsed': offer.date_parsed.strftime('%d.%m.%Y %H:%M')
            })
        
        # Характеристики
        attributes = []
        for attr in product.attributes:
            attributes.append({
                'name': attr.attribute_name,
                'value': attr.attribute_value
            })
        
        return jsonify({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.canonical_name,
                'description': product.description,
                'brand': product.brand,
                'model': product.model,
                'image_url': product.image_url or 'https://via.placeholder.com/300?text=No+Image'
            },
            'offers': offers,
            'attributes': attributes,
            'total_offers': len(offers)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@app.route('/api/stats')
def stats():
    """Статистика базы данных"""
    try:
        total_products = Product.query.count()
        total_offers = Offer.query.count()
        
        # Уникальные сайты
        websites = db.session.query(Offer.website_name).distinct().all()
        websites = [w[0] for w in websites]
        
        return jsonify({
            'success': True,
            'stats': {
                'total_products': total_products,
                'total_offers': total_offers,
                'websites': websites,
                'database': 'SQLite'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Запуск веб-приложения")
    print("🌐 Адрес: http://localhost:5000")
    print("📁 База данных: SQLite (products.db)")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)@app.route('/api/brands')
def get_brands():
    """Получение списка уникальных брендов"""
    try:
        from database.models import Product
        brands = db.session.query(Product.brand).filter(Product.brand.isnot(None)).distinct().all()
        brands = sorted([b[0] for b in brands if b[0]])
        return jsonify({'success': True, 'brands': brands})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/websites')
def get_websites():
    """Получение списка магазинов"""
    try:
        from database.models import Offer
        websites = db.session.query(Offer.website_name).distinct().all()
        websites = sorted([w[0] for w in websites if w[0]])
        return jsonify({'success': True, 'websites': websites})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})