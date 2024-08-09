FROM python:3.11-alpine
# kafka.admin doesn't work with python-3.12 https://github.com/dpkp/kafka-python/issues/2412

# for gcc required by aiokafka
RUN apk add build-base zlib-dev

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir

COPY src/ .

ENTRYPOINT ["gunicorn", "wsgi_app:app", "--log-level=debug", "-w", "4", "--bind", "0.0.0.0:8000"]
