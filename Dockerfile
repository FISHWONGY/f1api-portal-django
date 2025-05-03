FROM python:3.11-slim

WORKDIR /usr/src

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_VERSION=0.4.0 \
    UV_HTTP_TIMEOUT=1200

ENV PATH="/root/.local/bin:$PATH"

RUN pip install pipx
RUN pipx install uv==${UV_VERSION}

COPY . /usr/src/

RUN uv venv

ENV PATH="/usr/src/.venv/bin:$PATH"

RUN uv pip install -r pyproject.toml

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "f1apiportal.wsgi:application", "--bind", "0.0.0.0:8000"]