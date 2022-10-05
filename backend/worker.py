import time
import random

from celery import Celery

# Wait for rabbitmq to be started
print('Application started')

time.sleep(8)

print('Begin execution')


broker_url = 'amqp://waccproject:waccpassword@rabbitmq:5672'
backend_url = 'rpc://'

app = Celery(
    'celery_app',
    broker=broker_url,
    backend = backend_url
    
)


@app.task(name='addTask')  # Named task
def add(x, y):
    print('Task Add started')
    time.sleep(10 * random.random())  # Simulate a long task
    print('Task Add done')
    return x + y