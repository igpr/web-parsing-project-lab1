"""
Создание тестовых картинок для товаров
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Создаем папку если нет
os.makedirs('webapp/static/images/products', exist_ok=True)

# Цвета для разных категорий
category_colors = {
    'Ноутбуки': ('#4A90E2', '#FFFFFF'),
    'Смартфоны': ('#50E3C2', '#000000'),
    'Наушники': ('#B8E986', '#000000'),
    'Умные часы': ('#F5A623', '#000000'),
    'Планшеты': ('#BD10E0', '#FFFFFF'),
    'default': ('#333333', '#FFFFFF')
}

# Примеры товаров для картинок
sample_products = [
    {'name': 'Ноутбук ASUS', 'category': 'Ноутбуки'},
    {'name': 'Смартфон Samsung', 'category': 'Смартфоны'},
    {'name': 'Наушники Sony', 'category': 'Наушники'},
    {'name': 'Часы Apple Watch', 'category': 'Умные часы'},
    {'name': 'Планшет iPad', 'category': 'Планшеты'},
    {'name': 'Мышь Logitech', 'category': 'default'},
    {'name': 'Клавиатура Razer', 'category': 'default'},
    {'name': 'Монитор Dell', 'category': 'default'},
]

def create_product_image(product_name, category='default'):
    """Создает изображение для товара"""
    width, height = 300, 200
    bg_color, text_color = category_colors.get(category, category_colors['default'])
    
    # Создаем изображение
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    try:
        # Пробуем загрузить шрифт
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Если нет шрифта, используем стандартный
        font = ImageFont.load_default()
    
    # Разбиваем текст на строки
    words = product_name.split()
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= 20:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Рисуем текст
    y = (height - len(lines) * 30) // 2
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill=text_color, font=font)
        y += 30
    
    # Сохраняем
    filename = product_name.lower().replace(' ', '_').replace('/', '_')[:50] + '.png'
    filepath = f'webapp/static/images/products/{filename}'
    image.save(filepath)
    
    return filename

def main():
    """Создаем картинки для всех товаров"""
    print("Создаю тестовые картинки...")
    
    created = []
    for product in sample_products:
        filename = create_product_image(product['name'], product['category'])
        created.append(filename)
        print(f"  Создано: {filename}")
    
    # Создаем картинку по умолчанию
    image = Image.new('RGB', (300, 200), '#F0F0F0')
    draw = ImageDraw.Draw(image)
    draw.text((100, 90), "No Image", fill="#999999")
    image.save('webapp/static/images/no_image.png')
    print("  Создано: no_image.png")
    
    print(f"\n✅ Создано {len(created)} тестовых картинок")
    print("📍 Путь: webapp/static/images/products/")

if __name__ == "__main__":
    main()