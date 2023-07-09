FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /opt/auth

RUN apt update
RUN apt install -y python3-pip

COPY pyproject.toml pyproject.toml

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

COPY . .

ENV APP_MODULE="auth.main:auth"
ENV PYTHONPATH=/opt/auth

CMD ["/start-reload.sh"]