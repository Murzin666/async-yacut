import random
import string
from .models import URLMap


def get_unique_short_id():
    """Генерирует уникальный короткий идентификатор (6 символов)."""
    chars = string.ascii_letters + string.digits
    length = 6

    while True:
        short_id = ''.join(random.choice(chars) for _ in range(length))

        # Проверяем, что ID не равен 'files' (зарезервированный путь)
        if short_id == 'files':
            continue

        # Проверяем уникальность в БД
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id