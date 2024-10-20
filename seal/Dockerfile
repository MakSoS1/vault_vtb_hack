# Используем образ Python 3.9
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы приложения
COPY . .

# Команда для запуска скрипта auto-unseal
CMD ["python", "seal.py"]
