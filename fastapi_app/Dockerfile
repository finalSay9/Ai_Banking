FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ ./requirements/
RUN pip install --upgrade pip \
    && pip install -r requirements/fastapi.txt -r requirements/ml.txt

COPY fastapi_app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
