FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir pipenv

COPY backend/django/Pipfile backend/django/Pipfile.lock ./
RUN pipenv install --system --deploy

# Install production server and PostgreSQL adapter
RUN pip install --no-cache-dir gunicorn psycopg2-binary

COPY backend/django/ .

EXPOSE 8000

# Dual-stack bind via [::] so Railway's IPv6-only private network can reach us
# (Linux binds dual-stack by default; IPv4 clients still work via ::ffff:).
# Port is fixed at 8000 to match EXPOSE and the nginx upstream; Railway does
# not set $PORT for private-only services, so a literal 8000 is stable.
# `exec` gives gunicorn PID 1 so SIGTERM shuts it down cleanly on redeploys.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn imagi.wsgi:application --bind [::]:8000 --workers 3 --timeout 120"]
