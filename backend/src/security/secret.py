import os
import base64
from cryptography.fernet import Fernet

_KEY = os.getenv("ASTRO_SECRET_KEY")
if _KEY:
    fernet = Fernet(_KEY.encode())
else:
    fernet = None

def encrypt(value: str):
    if not fernet:
        return value
    return fernet.encrypt(value.encode()).decode()

def decrypt(value: str):
    if not fernet:
        return value
    return fernet.decrypt(value.encode()).decode()