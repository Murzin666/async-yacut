from flask import request, jsonify
from yacut import app, db
from .models import URLMap
from .utils import get_unique_short_id
from .error_handlers import InvalidAPIUsage
import re


def validate_request_data(data):
    """Проверка данных запроса."""
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)

    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!', 400)

    return data


def validate_url(original):
    """Проверка URL."""
    if not original.startswith(('http://', 'https://')):
        raise InvalidAPIUsage('Некорректный URL', 400)
    return original


def validate_custom_id(custom_id):
    """Проверка кастомного ID."""
    if not custom_id:
        return None

    if len(custom_id) > 16:
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки', 400)

    if not re.match(r'^[a-zA-Z0-9]+$', custom_id):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки', 400)

    if custom_id == 'files':
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.', 400)

    existing = URLMap.query.filter_by(short=custom_id).first()
    if existing:
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.', 400)

    return custom_id


def get_or_generate_short_id(custom_id):
    """Получить или сгенерировать короткий ID."""
    if custom_id:
        return validate_custom_id(custom_id)
    return get_unique_short_id()


def create_url_mapping(original, short_id):
    """Создать запись в БД."""
    url_map = URLMap(original=original, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    return url_map


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """POST /api/id/ - создание короткой ссылки."""
    try:
        data = request.get_json()
    except Exception:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)

    data = validate_request_data(data)
    original = validate_url(data['url'])

    custom_id = data.get('custom_id', '').strip()
    short_id = get_or_generate_short_id(custom_id)

    create_url_mapping(original, short_id)

    short_link = f"{request.host_url}{short_id}"

    return jsonify({
        'url': original,
        'short_link': short_link
    }), 201


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original_link(short_id):
    """GET /api/id/<short_id>/ - получение оригинальной ссылки."""
    url_map = URLMap.query.filter_by(short=short_id).first()

    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', 404)

    return jsonify({'url': url_map.original}), 200