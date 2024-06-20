FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "29543"]
