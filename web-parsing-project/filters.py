# filters.py
"""
Пользовательские фильтры для Jinja2
"""
from datetime import datetime

def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    """Форматирует дату для отображения в шаблонах"""
    if value is None:
        return ""
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f').strftime(format)

def register_filters(app):
    """Регистрирует фильтры в приложении Flask"""
    app.jinja_env.filters['datetimeformat'] = datetimeformat