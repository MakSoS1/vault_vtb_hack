# encryption.py
from cryptography.fernet import Fernet
from config import Config

cipher = Fernet(Config.ENCRYPTION_KEY)

def encrypt_secret(secret_value: str):
    """Шифрует значение секрета."""
    return cipher.encrypt(secret_value.encode()).decode()

def decrypt_secret(encrypted_value: str):
    """Дешифрует значение секрета."""
    return cipher.decrypt(encrypted_value.encode()).decode()
