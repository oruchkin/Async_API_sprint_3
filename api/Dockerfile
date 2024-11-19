FROM python:3.12-slim

WORKDIR /opt/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libffi-dev make libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir

COPY src/ ./src

EXPOSE 26452

ENTRYPOINT ["gunicorn", "src.main:app", "--log-level=debug", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
