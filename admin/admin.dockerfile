FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 4
ENV UWSGI_THREADS 8
ENV UWSGI_HARAKIRI 60
ENV DJANGO_SETTINGS_MODULE 'config.settings'

WORKDIR /opt/admin_init

COPY pyproject.toml pyproject.toml
RUN mkdir -p /opt/admin_init/static/ && \
    mkdir -p /opt/admin_init/media/  &&  \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

COPY uwsgi/uwsgi.ini uwsgi/uwsgi.ini
COPY . .

EXPOSE 8000

COPY ./entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
