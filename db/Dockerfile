FROM mongo:latest

RUN apt-get update && apt-get install -y python3 python3-pip

COPY create_db.py /data/create_db.py
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

# EXPOSE 27017

ENTRYPOINT python3 /data/create_db.py
