services:
  db:
    image: postgres:15-alpine
    container_name: fraud_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: fraud_redis
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  django_app:
    build:
      context: ./django_app
      dockerfile: Dockerfile
    container_name: fraud_django
    command: >
      gunicorn core.wsgi:application
      --bind 0.0.0.0:8000
      --workers ${GUNICORN_WORKERS:-3}
    volumes:
      - ./django_app:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_worker:
    build:
      context: ./django_app
      dockerfile: Dockerfile
    container_name: fraud_celery_worker
    command: celery -A core worker --loglevel=info
    volumes:
      - ./django_app:/app
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      django_app:
        condition: service_started

  celery_beat:
    build:
      context: ./django_app
      dockerfile: Dockerfile
    container_name: fraud_celery_beat
    command: celery -A core beat --loglevel=info
    volumes:
      - ./django_app:/app
      - celery_beat_data:/app/celerybeat
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      django_app:
        condition: service_started

  fastapi_app:
    build:
      context: ./fastapi_app
      dockerfile: Dockerfile
    container_name: fraud_fastapi
    command: >
      uvicorn main:app
      --host 0.0.0.0
      --port 8001
    env_file:
      - .env
    depends_on:
      redis:
        condition: service_healthy

  nginx:
    image: nginx:alpine
    container_name: fraud_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - django_app
      - fastapi_app

volumes:
  postgres_data:
  static_volume:
  media_volume:
  celery_beat_data:
