FROM python:3.8
ADD ./testcaller/requirements.txt /
RUN pip3 install -r requirements.txt
ADD ./celery_common /celery_common/
ADD ./testcaller/main.py /

ENTRYPOINT celery -A main worker --concurrency=1 --loglevel=info -n test_caller_worker.%h
