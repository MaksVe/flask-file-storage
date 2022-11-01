import hashlib


def get_hash(file_to_read, algorithm='sha256'):
    """Gets hash of a file.
    Supports sha1, sha256 and md5 algorithms.
    
    Args:
        file_to_read (FileStorage): Flask's FileStorage object
        algorithm (str): type of an algorithm (e.g. sha256)
        
    Returns:
        a string representation of a file hash"""

    hash_algorithms = {
        'sha1':     hashlib.sha1,
        'sha256':   hashlib.sha256,
        'md5':      hashlib.md5
    }

    filehash = hash_algorithms.get(algorithm)()

    for chunk in _read_in_chunks(file_to_read, 50 * 1048576):
        filehash.update(chunk)

    file_to_read.seek(0)

    return filehash.hexdigest()


def _read_in_chunks(file_object, chunk_size=1024):
    """Reads file object in chunks.
    
    Args:
        file_object (IO): opened file object
        chunk_size (int): a size of chunk in bytes
        
    Yields:
        a chunk of a read data from a file object"""

    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
