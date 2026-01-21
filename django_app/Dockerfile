FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ ./requirements/
RUN pip install --upgrade pip \
    && pip install -r requirements/django.txt -r requirements/ml.txt



CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
