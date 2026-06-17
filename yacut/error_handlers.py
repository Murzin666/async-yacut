from flask import jsonify, render_template, request
from yacut import app, db


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {'message': self.message}


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(400)
def bad_request(error):
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Некорректный запрос'}), 400
    return render_template('error.html', error_code=400,
                           error_message='Некорректный запрос'), 400


@app.errorhandler(404)
def page_not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Указанный id не найден'}), 404
    return render_template('error.html', error_code=404,
                           error_message='Страница не найдена'), 404


@app.errorhandler(405)
def method_not_allowed(error):
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Метод не разрешен'}), 405
    return render_template('error.html', error_code=405,
                           error_message='Метод не разрешен'), 405


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Внутренняя ошибка сервера'}), 500
    return render_template('error.html', error_code=500,
                           error_message='Внутренняя ошибка сервера'), 500