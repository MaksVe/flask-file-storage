import os
from pathlib import Path
from flask import (
    request, jsonify, send_from_directory, Blueprint, current_app, abort
)

from file_storage import db
from file_storage.get_file_hash import get_hash
from file_storage.auth import require_auth

bp = Blueprint('storage', __name__)


@bp.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    # Check if file is in the request
    if 'file' not in request.files:
        abort(400, 'file is required')

    file = request.files['file']
    # Generate file information
    file_hash = get_hash(file, 'md5')
    file_folder_name = file_hash[:2]
    file_upload_path = Path(current_app.config['STORAGE'], file_folder_name)
    file_full_path = Path(file_upload_path, file_hash)
    file_owner = request.authorization.username

    # Create file upload directory
    Path(file_upload_path).mkdir(parents=True, exist_ok=True)

    # Save file
    file.save(file_full_path)

    # Save file information in database
    db.save_upload_in_db(
        str(file_hash),
        str(file_folder_name),
        str(file_upload_path),
        str(file_full_path),
        str(file_owner)
    )

    return jsonify({'Successfully stored': file_hash}), 201


@bp.route('/delete', methods=['POST'])
@require_auth
def delete_file():
    file_hash = request.form['file_hash']

    # Get upload from database
    upload = db.get_upload_from_db(file_hash)

    # Check if file exists
    if not upload:
        abort(404, 'File not found')

    # Remove file
    try:
        os.remove(upload['file_full_path'])
        # Remove file folder if it's empty
        if not any(Path(upload['file_upload_path']).iterdir()):
            os.rmdir(Path(upload['file_upload_path']))
    except OSError as e:
        print("Error: %s - %s" % (e.filename, e.strerror))

    # Remove upload from database
    db.remove_upload_from_db(file_hash)

    return jsonify({'Successfully deleted': file_hash}), 200


@bp.route('/download', methods=['GET'])
def download_file():
    file_hash = request.form['file_hash']

    # Get upload from database
    upload = db.get_upload_from_db(file_hash)

    # Check if file exists
    if not upload:
        abort(404, 'File not found')

    # Return file
    return send_from_directory(
        Path(upload['file_upload_path']), upload['file_hash']
    )
