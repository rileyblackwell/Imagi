FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

# Install production server and PostgreSQL adapter
RUN pip install --no-cache-dir gunicorn psycopg2-binary

COPY . .

EXPOSE 8000

CMD ["gunicorn", "imagi.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
