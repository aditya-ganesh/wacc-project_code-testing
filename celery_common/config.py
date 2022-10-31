import os

env = os.environ

RABBITMQ_USER   = os.environ['RABBITMQ_DEFAULT_USER']
RABBITMQ_PWD    = os.environ['RABBITMQ_DEFAULT_PASS']
RABBITMQ_PORT   = os.environ['RABBITMQ_DEFAULT_PORT']
RABBITMQ_HOST   = "rabbitmq"

broker_url = f'pyamqp://{RABBITMQ_USER}:{RABBITMQ_PWD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}'
result_backend = 'rpc://'
task_acks_late = True
