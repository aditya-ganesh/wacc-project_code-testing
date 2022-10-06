import time
import random
import logging

from celery import Celery

# Wait for rabbitmq to be started

logging.warning('Application started')

time.sleep(10)

logging.warning('Begin execution')


broker_url = 'amqp://waccproject:waccpassword@rabbitmq:25672'
backend_url = 'rpc://'

app = Celery(
    'celery_app',
    broker=broker_url,
    backend = backend_url
    
)


numTasks = 10
tasks = []

for i in range(numTasks):
    time.sleep(2 * random.random())  # Random delay
    tasks.append(
        app.send_task('addTask', (i, 3))  # Send task by name
    )
    logging.warning('Sent task: {}'.format(i))

for task in tasks:
    result = task.get()
    logging.warning('Received result: {}'.format(result) )

logging.warning('Application ended')