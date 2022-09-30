FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install virtualenv ipykernel numpy pandas pika
COPY backend.py /data/backend.py
ENTRYPOINT python3 /data/backend.py
