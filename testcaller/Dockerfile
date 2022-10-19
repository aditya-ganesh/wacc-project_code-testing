FROM python:3.8
ADD ./testcaller/requirements.txt /
ADD ./testcaller/main.py /
ADD ./celery_common /celery_common/
RUN pip3 install -r requirements.txt
ENTRYPOINT celery -A main worker --concurrency=1 --loglevel=info -n test_caller_worker.%h