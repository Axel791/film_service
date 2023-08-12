FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /opt/app

RUN apt update
RUN apt install -y python3-pip

COPY pyproject.toml pyproject.toml

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

COPY . .

ENV APP_MODULE="app.main:app"
ENV PYTHONPATH=/opt/app

COPY init_kafka.sh /init_kafka.sh
RUN chmod u+x /init_kafka.sh

CMD ["/start-reload.sh"]