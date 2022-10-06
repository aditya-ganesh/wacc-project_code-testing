import subprocess
import logging
import time
import json

logging.basicConfig(level=logging.INFO)

from celery import Celery

rabbitmq_user = 'waccproject'
rabbitmq_pass = 'waccpassword'
rabbitmq_port = 5672

broker_url = f'amqp://{rabbitmq_user}:{rabbitmq_pass}@rabbitmq:{rabbitmq_port}'
backend_url = 'rpc://'

celery_app = Celery(
    'celery_app',
    broker=broker_url,
    backend = backend_url
    
)





@celery_app.task(name='processPython')
def procesPython(code_id,code_lines):


    logging.info(" [x] Received {}, {}".format(code_id,code_lines) )

    with open(f'{code_id}.py','w') as codefile:
        codefile.writelines(code_lines)

    logfile = open('log.txt','w')
    errfile = open('err.txt','w')
    ret = subprocess.run(['python3', f'{code_id}.py'],stdout=logfile,stderr=errfile)


    if ret.returncode == 0:
        exec_status = "Code executed successfully"
        with open('log.txt','r') as log:
            exec_output = log.read()


    else:
        exec_status = "Code execution failed"
        with open('err.txt','r') as err:
            exec_output = err.read()

    exec_params = {
        'retcode'     : ret.returncode,  
        'exec_status' : exec_status,
        'exec_output' : exec_output
    }

    logging.info(" [x] Sending return params {}".format(exec_params) )

    return exec_params
