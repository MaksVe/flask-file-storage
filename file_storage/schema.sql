DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS uploads;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE uploads (
    file_hash TEXT NOT NULL,
    file_folder_name TEXT NOT NULL,
    file_upload_path TEXT NOT NULL,
    file_full_path TEXT NOT NULL,
    file_owner TEXT NOT NULL
);