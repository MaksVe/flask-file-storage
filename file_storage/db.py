import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash



def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

    create_admin()
    click.echo('username: admin password: admin')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def create_admin():
    db = get_db()

    db.execute(
        'INSERT INTO user (username, password)'
        ' VALUES (?, ?)',
        ('admin', generate_password_hash('admin'))
    )
    db.commit()


def save_upload_in_db(file_hash,
                      file_folder_name,
                      file_upload_path,
                      file_full_path,
                      file_owner):
    db = get_db()
    db.execute(
        'INSERT INTO uploads (file_hash, file_folder_name, file_upload_path, '
        'file_full_path, file_owner)'
        ' VALUES (?, ?, ?, ?, ?)',
        (file_hash, file_folder_name, file_upload_path, file_full_path, file_owner)
    )
    db.commit()


def remove_upload_from_db(file_hash):
    db = get_db()
    db.execute(
        'DELETE FROM uploads WHERE file_hash = ?',
        (file_hash,)
    )
    db.commit()


def get_upload_from_db(file_hash):
    db = get_db()
    upload = db.execute(
        'SELECT file_owner, file_upload_path, file_full_path, file_hash'
        ' FROM uploads WHERE file_hash = ?',
        (file_hash,)
    ).fetchone()
    
    return upload