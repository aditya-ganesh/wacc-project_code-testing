FROM python:3.8
ADD ./dbhandler/requirements.txt /
RUN pip3 install -r requirements.txt
ADD ./celery_common /celery_common/
ADD ./dbhandler/main.py /

ENTRYPOINT celery -A main worker --concurrency=4 --loglevel=info -n database_handler_worker.%h
