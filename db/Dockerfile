FROM mongo:latest

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install pymongo[srv]
COPY create_db.py /data/create_db.py

EXPOSE 27017

ENTRYPOINT python3 /data/create_db.py
