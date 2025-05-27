FROM python:3.13-slim

# Установка критических зависимостей для psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /site_app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .

# Установка psycopg2 через binary-версию
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . .

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /site_app
USER appuser

# # Команды для миграций
RUN python manage.py makemigrations
# COPY entrypoint.sh .
# RUN chmod +x entrypoint.sh
# ENTRYPOINT ["./entrypoint.sh"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# RUN python manage.py runbot
CMD ["bash", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 myproject.asgi:application"]

