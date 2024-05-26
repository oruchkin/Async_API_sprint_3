FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt requirements.txt
RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir
COPY . .
RUN python ./manage.py collectstatic --noinput


FROM nginx:1.25-alpine as nginx
COPY --from=builder /app/static /data/static