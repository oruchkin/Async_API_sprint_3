FROM python:3.10

WORKDIR /opt/app

ENV DJANGO_SETTINGS_MODULE=config.settings

COPY ../../app/requirements.txt requirements.txt
RUN  pip install --upgrade pip \
     && pip install -r requirements.txt \
     && pip install uwsgi

COPY ../../app/ .

RUN chmod +x entrypoint.sh

ADD https://github.com/vishnubob/wait-for-it/raw/master/wait-for-it.sh /usr/wait-for-it.sh
RUN chmod +x /usr/wait-for-it.sh


EXPOSE 8000/tcp

ENTRYPOINT ["./entrypoint.sh"]
