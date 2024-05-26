FROM python:3.10

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt /app/requirements.txt
WORKDIR /app


RUN ls -la /app
RUN ls -la
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN chmod +x init_db.sh

ENTRYPOINT ["/app/init_db.sh"]
