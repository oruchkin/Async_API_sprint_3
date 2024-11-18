FROM python:3.10-alpine

RUN apk update && apk add postgresql-client

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


RUN ls -la

COPY . .
RUN chmod +x init_db.sh

ENTRYPOINT ["python", "/app/load_data.py"]
