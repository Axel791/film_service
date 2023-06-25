FROM python:3.10

WORKDIR /opt/tests

RUN apt update
RUN apt install -y python3-pip

COPY pyproject.toml pyproject.toml

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main

COPY . .

ENV PYTHONPATH=/opt/tests

CMD ["sh", "run_tests.sh"]