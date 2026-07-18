FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Node.js and Chromium power the Build workspace preview: generated user
# projects run their Vite + Django dev servers inside this container, and a
# headless Chromium renders them for the workspace UI — the same setup used
# in local development, which is what makes preview work on Railway.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs chromium \
    && rm -rf /var/lib/apt/lists/*

ENV BROWSER_PREVIEW_EXECUTABLE=/usr/bin/chromium

RUN pip install --no-cache-dir pipenv

COPY backend/django/Pipfile backend/django/Pipfile.lock ./
RUN pipenv install --system --deploy

# Install servers and PostgreSQL adapter. Kept out of the Pipfile (as gunicorn
# and psycopg2 already are) so adding them cannot re-lock the whole dependency
# graph. Local dev needs uvicorn too, for streaming to behave as it does here:
#   pipenv run pip install "uvicorn[standard]"
RUN pip install --no-cache-dir gunicorn "uvicorn[standard]" psycopg2-binary

COPY backend/django/ .

# Prewarm the shared frontend dependency store. Every generated user project
# ships the same frontend package.json, so we install that dependency set once
# here and bake the resulting node_modules into the image. Generated projects
# then symlink their node_modules at this store instead of each running their
# own npm install — instant project creation/preview, and the install persists
# across redeploys instead of being repeated on every rebuild. Docker layer
# caching skips this step entirely when the dependency set is unchanged.
#
# DJANGO_SECRET_KEY is a throwaway value only needed so settings import during
# the build; it never reaches the running image. FRONTEND_DEP_STORE_ROOT is
# also set as a runtime ENV below so the store is found at the same path.
ENV FRONTEND_DEP_STORE_ROOT=/opt/imagi/frontend-deps
RUN DJANGO_SECRET_KEY=build-time-only python manage.py warm_frontend_deps

EXPOSE 8000

# Shell form so $PORT expands at runtime (Railway assigns it dynamically).
# ASGI via uvicorn workers: agent runs stream over SSE for minutes, which sync
# workers cannot hold open (one run would occupy a whole worker, and gunicorn
# would kill it at --timeout since sync workers do not heartbeat mid-request).
CMD python manage.py migrate --noinput && \
    gunicorn imagi.asgi:application \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind "[::]:${PORT:-8000}" \
        --workers 3 \
        --timeout 120
