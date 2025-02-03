# Указываем базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект в контейнер
COPY clinic /app

# Устанавливаем переменную окружения для Django
ENV PYTHONUNBUFFERED=1

# Выполняем миграции и запускаем сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
