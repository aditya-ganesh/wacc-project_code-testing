FROM python:3.8
ADD ./dbhandler/requirements.txt /
ADD ./dbhandler/main.py /
ADD ./celery_common /celery_common/
RUN pip3 install -r requirements.txt
ENTRYPOINT celery -A main worker --concurrency=4 --loglevel=info -n database_handler_worker.%h