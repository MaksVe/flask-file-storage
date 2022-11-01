import io
import pytest
import base64
from pathlib import Path

from file_storage.db import get_db


@pytest.mark.parametrize('path', (
    '/upload',
    '/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.status_code == 401


@pytest.mark.parametrize('path', (
    '/upload',
    '/delete',
))
def test_invalid_credentials(client, path):
    credentials = base64.b64encode(b"test:wrong").decode('utf-8')
    response = client.post(
        path,
        headers={"Authorization": "Basic {}".format(credentials)}
    )
    assert response.status_code == 401


@pytest.mark.parametrize('path', (
    '/upload',
    '/delete',
))
def test_user_not_found(client, path):
    credentials = base64.b64encode(b"alien:user").decode('utf-8')
    response = client.post(
        path,
        headers={"Authorization": "Basic {}".format(credentials)}
    )
    assert response.status_code == 401


def test_upload(client, app):
    credentials = base64.b64encode(b"test:test").decode('utf-8')
    data = {'file': (io.BytesIO(b"abcdef"), 'test_file')}
    response = client.post(
        '/upload',
        headers={"Authorization": "Basic {}".format(credentials)},
        data=data
    )
    assert response.status_code == 201

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(file_hash) FROM uploads').fetchone()[0]
        assert count == 2


def test_upload_file_is_required(client):
    credentials = base64.b64encode(b"test:test").decode('utf-8')
    response = client.post(
        '/upload',
        headers={"Authorization": "Basic {}".format(credentials)}
    )
    assert response.status_code == 400


def test_download(client, app, test_file):    
    file_hash = 'test_file'
    _create_test_file_in_db(app, file_hash, test_file)

    data = {'file_hash': file_hash}
    response = client.get(
        '/download',
        data=data)
    assert response.status_code == 200


def test_download_nonexistent_file(client):
    file_hash = 'test_file'

    data = {'file_hash': file_hash}
    response = client.get(
        '/download',
        data=data)
    assert response.status_code == 404


def test_delete(client, app, test_file):
    file_hash = 'test_file'
    _create_test_file_in_db(app, file_hash, test_file)

    credentials = base64.b64encode(b"test:test").decode('utf-8')
    data = {'file_hash': file_hash}
    response = client.post(
        '/delete',
        headers={"Authorization": "Basic {}".format(credentials)},
        data=data)
    assert response.status_code == 200


def _create_test_file_in_db(app, file_hash, test_file):
    file_upload_path = Path(test_file).parent
    file_full_path = Path(test_file)

    with app.app_context():
        db = get_db()
        db.execute(
            'INSERT INTO uploads (file_hash, file_folder_name, file_upload_path,'
            ' file_full_path, file_owner)'
            ' VALUES (?, ?, ?, ?, ?)',
            (str(file_hash),'.', str(file_upload_path), str(file_full_path), 'test')
        )
        db.commit()