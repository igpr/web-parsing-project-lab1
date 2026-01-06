"""
Инициализация базы данных SQLite
"""
from models import db
from flask import Flask

def init_database():
    """Создаем таблицы в SQLite базе"""
    app = Flask(__name__)
    
    # SQLite база будет в файле products.db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        print("✅ База данных создана в файле 'products.db'")
        print("✅ Таблицы: products, offers, product_attributes")
        
        # Добавляем тестовые данные
        from datetime import datetime
        
        # Проверяем, есть ли уже данные
        from models import Product
        if Product.query.count() == 0:
            print("📝 Добавляем тестовые данные...")
            
            # Тестовый продукт 1
            product1 = Product(
                canonical_name="Ноутбук ASUS VivoBook 15",
                description="15.6-дюймовый ноутбук с процессором Intel Core i5",
                brand="ASUS",
                model="VivoBook 15 X515EA",
                image_url="https://via.placeholder.com/300",
                created_at=datetime.utcnow()
            )
            db.session.add(product1)
            db.session.flush()
            
            # Предложения для продукта 1
            from models import Offer, ProductAttribute
            offer1 = Offer(
                product_id=product1.id,
                website_name="DNS",
                price=54990.0,
                url="https://www.dns-shop.ru/product/asus-vivobook-15",
                date_parsed=datetime.utcnow(),
                in_stock=True
            )
            
            offer2 = Offer(
                product_id=product1.id,
                website_name="MVideo",
                price=56990.0,
                url="https://www.mvideo.ru/asus-vivobook-15",
                date_parsed=datetime.utcnow(),
                in_stock=True
            )
            
            # Характеристики
            attr1 = ProductAttribute(
                product_id=product1.id,
                attribute_name="Диагональ экрана",
                attribute_value="15.6 дюймов"
            )
            
            attr2 = ProductAttribute(
                product_id=product1.id,
                attribute_name="Процессор",
                attribute_value="Intel Core i5-1135G7"
            )
            
            attr3 = ProductAttribute(
                product_id=product1.id,
                attribute_name="Оперативная память",
                attribute_value="8 ГБ"
            )
            
            db.session.add_all([offer1, offer2, attr1, attr2, attr3])
            
            # Тестовый продукт 2
            product2 = Product(
                canonical_name="Смартфон Samsung Galaxy A54",
                description="Смартфон с AMOLED экраном и камерой 50 МП",
                brand="Samsung",
                model="Galaxy A54",
                image_url="https://via.placeholder.com/300",
                created_at=datetime.utcnow()
            )
            db.session.add(product2)
            db.session.flush()
            
            offer3 = Offer(
                product_id=product2.id,
                website_name="Citilink",
                price=32990.0,
                url="https://www.citilink.ru/samsung-galaxy-a54",
                date_parsed=datetime.utcnow(),
                in_stock=True
            )
            
            attr4 = ProductAttribute(
                product_id=product2.id,
                attribute_name="Экран",
                attribute_value="6.4 дюйма, Super AMOLED"
            )
            
            attr5 = ProductAttribute(
                product_id=product2.id,
                attribute_name="Камера",
                attribute_value="Основная 50 МП + сверхширокая 12 МП"
            )
            
            db.session.add_all([offer3, attr4, attr5])
            
            db.session.commit()
            print("✅ Добавлено 2 тестовых товара с предложениями")
        else:
            print("ℹ️ В базе уже есть данные")
        
        # Статистика
        from models import Product, Offer
        total_products = Product.query.count()
        total_offers = Offer.query.count()
        print(f"\n📊 Статистика:")
        print(f"   Товаров: {total_products}")
        print(f"   Предложений: {total_offers}")

if __name__ == "__main__":
    init_database()