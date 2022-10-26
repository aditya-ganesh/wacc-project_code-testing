FROM mongo:latest

RUN apt-get update && apt-get install -y python3 python3-pip
COPY ./dbinit/requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY ./dbinit/create_db.py /data/create_db.py

WORKDIR /data

ENTRYPOINT python3 create_db.py


