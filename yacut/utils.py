import random
import string
from .models import URLMap


def get_unique_short_id():
    """Генерирует уникальный короткий идентификатор (6 символов)."""
    chars = string.ascii_letters + string.digits
    length = 6

    max_attempts = 100
    attempts = 0

    while attempts < max_attempts:
        short_id = ''.join(random.choice(chars) for _ in range(length))

        if not URLMap.query.filter_by(short=short_id).first():
            if short_id != 'files':
                return short_id

        attempts += 1

    return get_unique_short_id()