FROM python:3.10

WORKDIR /opt/app

ENV DJANGO_SETTINGS_MODULE=config.settings

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt \
     && pip install uwsgi

COPY . .

RUN python manage.py migrate
RUN #python manage.py collectstatic

EXPOSE 8000/tcp

ENTRYPOINT ["uwsgi", "--ini", "uwsgi.ini"]
