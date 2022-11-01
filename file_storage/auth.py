from functools import wraps
from flask import request, abort
from werkzeug.security import check_password_hash

from file_storage.db import get_db


def check_credentials(username, password):
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        abort(401, 'User not found')

    return username == user['username'] and check_password_hash(user['password'], password)


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth:
            abort(401, "Authorization is required")
        elif not check_credentials(auth.username, auth.password):
            abort(401, "Invalid credentials")

        return f(*args, **kwargs)
    return wrapper