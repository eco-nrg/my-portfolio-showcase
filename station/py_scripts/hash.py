import hashlib


def get_hash_value(string_value: str):
    hash_object = hashlib.md5(string_value.encode())
    return hash_object.hexdigest()
