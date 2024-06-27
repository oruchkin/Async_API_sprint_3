#The base image for the container 
FROM python:3.12-slim-bullseye
 
# Keeps Python from generating .pyc files in the container 
ENV PYTHONDONTWRITEBYTECODE=1 
 
# Turns off buffering for easier container logging 
ENV PYTHONUNBUFFERED=1 

RUN apt-get update \
&& apt-get install -y --no-install-recommends git \
&& apt-get purge -y --auto-remove \
&& rm -rf /var/lib/apt/lists/* \
&& git config --global core.autocrlf true

# Copy python requirements to the docker container and install
COPY admin/requirements.txt .
RUN python -m pip install -r requirements.txt 

COPY api/requirements.txt . 
RUN python -m pip install -r requirements.txt 

COPY api/tests/functional/requirements.txt .
RUN python -m pip install -r requirements.txt

COPY etl/requirements.txt .
RUN python -m pip install -r requirements.txt

COPY file_service/requirements.txt .
RUN python -m pip install -r requirements.txt

COPY idp/requirements.txt .
RUN python -m pip install -r requirements.txt

#create a non root user to access the container
RUN adduser -u 5678 --disabled-password --gecos "" vscode