from typing import Any, List

from cryptography.fernet import Fernet

from equigest.settings import Settings

settings = Settings()
FERNET_SECRET_KEY = settings.FERNET_SECRET_KEY

fernet = Fernet(FERNET_SECRET_KEY.encode('utf-8'))

def encrypt_data(data: str):
    return fernet.encrypt(data.encode()).decode()

def uncrypt_data(data: str):
    return fernet.decrypt(data.encode()).decode()

def process_fields(instance: Any, fields: List[str], processor: callable):
    for field in fields:
        value = getattr(instance, field, None)
        if value:
            setattr(instance, field, processor(value))

def encrypt_fields(instance: Any, fields: List[str]):
    process_fields(instance, fields, encrypt_data)

def uncrypt_fields(instance: Any, fields: List[str]):
    process_fields(instance, fields, uncrypt_data)