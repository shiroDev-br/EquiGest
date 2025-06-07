from typing import Any, List

from cryptography.fernet import Fernet

from equigest.settings import Settings

settings = Settings()
SECRET_KEY = settings.SECRET_KEY

fernet = Fernet(SECRET_KEY)

def encrypt_data(data: str):
    byte_data = data.encode('utf-8')

    return fernet.encrypt(byte_data)

def uncrypt_data(data: str):
    return fernet.decrypt(data).decode('utf-8')

def process_fields(instance: Any, fields: List[str], processor: callable):
    for field in fields:
        value = getattr(instance, field, None)
        if value:
            setattr(instance, field, processor(value))

def encrypt_fields(instance: Any, fields: List[str]):
    process_fields(instance, fields, encrypt_data)

def uncrypt_fields(instance: Any, fields: List[str]):
    process_fields(instance, fields, uncrypt_data)