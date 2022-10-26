FROM python:3.8
ADD ./testrunner/requirements.txt /
RUN pip3 install -r requirements.txt
ADD ./celery_common /celery_common/
ADD ./testrunner/main.py /

ENTRYPOINT celery -A main worker --concurrency=1 --loglevel=info --soft-time-limit 10 --autoscale 10,0 -n test_runner_worker.%h
