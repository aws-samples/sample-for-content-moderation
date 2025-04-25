import hashlib

def get_unique_value(input_string):
    input_bytes = input_string.encode('utf-8')

    sha256_hash = hashlib.sha256()

    sha256_hash.update(input_bytes)

    unique_value = sha256_hash.hexdigest()

    return unique_value