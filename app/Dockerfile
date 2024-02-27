FROM python:3.9-alpine

# Time
ENV TZ Europe/Prague

# Python optimalisations
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Celery setup
ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

# Flask setup
ENV HOST 0.0.0.0
ENV PORT 5000

COPY . /app
WORKDIR /app

RUN apk add chromium
RUN apk add chromium-chromedriver

# Set display port to avoid crash
ENV DISPLAY=:99

# Instaling requirements
RUN pip install -U setuptools pip
RUN pip install -r requirements.txt

EXPOSE 5000

# Runing GuniCORN for web server
RUN pip install gunicorn

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]
