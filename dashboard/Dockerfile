FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-pip iputils-ping
COPY requirements.txt /data/requirements.txt
RUN pip install -r /data/requirements.txt

COPY dashboard.py /data/dashboard.py

ENTRYPOINT streamlit run /data/dashboard.py  --server.port 80
