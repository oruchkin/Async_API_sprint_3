FROM python:3.11

WORKDIR /etl
ENV PYTHONPATH="/etl"


COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "./main.py"]
