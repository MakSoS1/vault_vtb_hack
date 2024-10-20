# config.py
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_jwt_secret_key")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your_default_encryption_key")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ALGORITHM = "HS256"
