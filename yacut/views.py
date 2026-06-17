from flask import render_template, redirect, request, flash
from yacut import app, db
from .models import URLMap
from .forms import URLForm, FileUploadForm
from .utils import get_unique_short_id
import aiohttp
import asyncio


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница - создание короткой ссылки."""
    form = URLForm()
    short_url = None
    original = None

    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = (
            form.custom_id.data.strip()
            if form.custom_id.data
            else None
        )

        short_id = custom_id if custom_id else get_unique_short_id()

        existing = URLMap.query.filter_by(short=short_id).first()
        if existing:
            flash(
                'Предложенный вариант короткой ссылки уже существует.',
                'danger'
            )
            return render_template('index.html', form=form)

        url_map = URLMap(original=original, short=short_id)
        db.session.add(url_map)
        db.session.commit()

        short_url = f"{request.host_url}{short_id}"

        return render_template(
            'index.html',
            form=form,
            short_url=short_url,
            original=original
        )

    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    """Страница загрузки файлов на Яндекс Диск."""
    form = FileUploadForm()
    uploaded_files = []

    if form.validate_on_submit():
        files = request.files.getlist('files')

        if files and all(f.filename for f in files):
            uploaded_files = asyncio.run(upload_files_to_disk(files))

            for file_info in uploaded_files:
                has_short_id = 'short_id' in file_info
                if has_short_id and file_info.get('disk_url'):
                    url_map = URLMap(
                        original=file_info['disk_url'],
                        short=file_info['short_id'],
                        is_file=True
                    )
                    db.session.add(url_map)
                    short_link = f"{request.host_url}{file_info['short_id']}"
                    file_info['short_link'] = short_link

            db.session.commit()

            errors = [f for f in uploaded_files if 'error' in f]
            if errors:
                error_names = ', '.join([e['filename'] for e in errors])
                flash(
                    f'Некоторые файлы не загружены: {error_names}',
                    'warning'
                )
            else:
                flash('Все файлы успешно загружены!', 'success')
        else:
            flash('Выберите файлы для загрузки.', 'warning')

    return render_template(
        'files.html',
        form=form,
        uploaded_files=uploaded_files
    )


@app.route('/<short_id>')
def redirect_to_url(short_id):
    """Переадресация по короткой ссылке."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)


async def upload_files_to_disk(files):
    """Асинхронная загрузка файлов на Яндекс Диск."""
    disk_token = app.config['DISK_TOKEN']

    if not disk_token:
        return [
            {
                'filename': f.filename,
                'error': 'Не настроен токен Яндекс Диска'
            }
            for f in files
        ]

    async with aiohttp.ClientSession() as session:
        tasks = [
            upload_single_file(session, file, disk_token)
            for file in files
        ]
        results = await asyncio.gather(*tasks)

    return results


async def upload_single_file(session, file, disk_token):
    """Загрузка одного файла на Яндекс Диск."""
    headers = {'Authorization': f'OAuth {disk_token}'}
    filename = file.filename

    try:
        upload_url = (
            'https://cloud-api.yandex.net/v1/disk/resources/upload'
        )
        params = {'path': f'YaCut/{filename}', 'overwrite': 'true'}

        async with session.get(
            upload_url, headers=headers, params=params
        ) as resp:
            if resp.status != 200:
                return {
                    'filename': filename,
                    'error': 'Ошибка получения URL для загрузки'
                }
            data = await resp.json()
            href = data.get('href')

        if not href:
            return {
                'filename': filename,
                'error': 'Не получен URL для загрузки'
            }

        file_content = file.read()
        async with session.put(href, data=file_content) as resp:
            if resp.status not in [201, 202]:
                return {
                    'filename': filename,
                    'error': f'Ошибка загрузки: статус {resp.status}'
                }

        short_id = get_unique_short_id()
        download_url = (
            'https://cloud-api.yandex.net/v1/disk/resources/download'
        )
        params = {'path': f'YaCut/{filename}'}

        async with session.get(
            download_url, headers=headers, params=params
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                disk_url = data.get('href', '')
            else:
                disk_url = ''

        return {
            'filename': filename,
            'short_id': short_id,
            'disk_url': disk_url
        }

    except Exception as e:
        return {
            'filename': filename,
            'error': f'Ошибка: {str(e)}'
        }