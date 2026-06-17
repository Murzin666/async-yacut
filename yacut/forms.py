from flask_wtf import FlaskForm
from wtforms import StringField, MultipleFileField
from wtforms.validators import (
    DataRequired,
    URL,
    Length,
    Regexp,
    ValidationError
)
from .models import URLMap


class URLForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Введите корректный URL')
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(max=16, message='Не более 16 символов'),
            Regexp(
                r'^[a-zA-Z0-9]+$',
                message='Только латинские буквы и цифры'
            )
        ]
    )

    def validate_custom_id(self, field):
        if field.data:
            existing = URLMap.query.filter_by(short=field.data).first()
            if existing:
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            if field.data == 'files':
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        'Файлы', validators=[DataRequired(message='Выберите файлы')])