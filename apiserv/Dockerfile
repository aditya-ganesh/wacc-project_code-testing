FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-pip

COPY ./apiserv/apiserv.py /data/apiserv.py
COPY ./apiserv/requirements.txt /data/requirements.txt
COPY ./celery_common /data/celery_common

RUN pip install -r /data/requirements.txt

WORKDIR /data

ENTRYPOINT uvicorn apiserv:api_app --host 0.0.0.0
