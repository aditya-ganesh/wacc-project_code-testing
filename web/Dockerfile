FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt /data/requirements.txt
RUN pip install -r /data/requirements.txt

COPY web.py /data/web.py

ENTRYPOINT streamlit run /data/web.py
