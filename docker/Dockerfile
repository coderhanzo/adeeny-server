# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12.4
FROM python:${PYTHON_VERSION}-slim-bullseye AS base

ENV APP_HOME=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update && apt-get install -y \
    gcc \
    binutils \
    libproj-dev \
    gdal-bin \
    pkg-config \
    libpq-dev \
    libmagic1 \
    proj-bin \
    proj-data \
    default-libmysqlclient-dev \
    default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_HOME

RUN pip3 install --upgrade pip && pip3 install wheel && pip3 install poetry && pip3 install mysqlclient
COPY pyproject.toml poetry.lock ./

# Install Poetry environment
RUN poetry config virtualenvs.create false && poetry install && rm -rf $POETRY_CACHE_DIR

# COPY ./docker/entry /entry
# RUN sed -i 's/\r$//g' /entry
# RUN chmod +x /entry

# COPY ./docker/build /build
# RUN sed -i 's/\r$//g' /build
# RUN chmod +x /build

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
