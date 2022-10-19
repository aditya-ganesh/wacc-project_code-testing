FROM mongo:latest

COPY ./dbinit/setup.sh /data/setup.sh

RUN apt-get update && apt-get install -y python3 python3-pip

COPY ./dbinit/create_db.py /data/create_db.py

COPY ./dbinit/requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR /data

ENTRYPOINT python3 create_db.py


