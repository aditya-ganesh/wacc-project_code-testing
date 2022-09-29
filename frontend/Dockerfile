FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install virtualenv ipykernel numpy pandas streamlit pika
COPY frontend.py /data/frontend.py
EXPOSE 8501
ENTRYPOINT streamlit run /data/frontend.py
