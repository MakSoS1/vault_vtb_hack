# seal.py
import os
from cryptography.fernet import Fernet

# Генерация и загрузка ключа
def generate_key():
    key = Fernet.generate_key()
    with open("secret_key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret_key.key", "rb").read()

# Функция Auto-unseal (загружает ключ при старте)
def auto_unseal():
    if not os.path.exists("secret_key.key"):
        print("Generating new encryption key...")
        generate_key()
    else:
        print("Loading existing encryption key...")
    return load_key()

encryption_key = auto_unseal()
cipher = Fernet(encryption_key)
