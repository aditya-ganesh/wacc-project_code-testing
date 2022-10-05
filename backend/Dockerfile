FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install virtualenv ipykernel numpy pandas pika celery
WORKDIR /app
COPY worker.py .
ENTRYPOINT celery -A worker worker --autoscale 10 --loglevel=info
