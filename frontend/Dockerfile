FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install virtualenv ipykernel numpy pandas streamlit pika celery
COPY frontend.py /data/frontend.py
EXPOSE 8501
ENTRYPOINT python3 /data/frontend.py
