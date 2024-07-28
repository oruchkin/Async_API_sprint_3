FROM python:3.12-alpine

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir

COPY src/ .

EXPOSE 26452

ENTRYPOINT ["gunicorn", "wsgi_app:app", "--log-level=debug", "-w", "4", "--bind", "0.0.0.0:8000"]
