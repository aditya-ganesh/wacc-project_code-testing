import subprocess
import logging
import time
import json
import os

import motor
import motor.motor_asyncio
import asyncio 
import nest_asyncio

logging.basicConfig(level=logging.INFO)

from celery import Celery

rabbitmq_user = os.environ['RABBITMQ_DEFAULT_USER']
rabbitmq_pass = os.environ['RABBITMQ_DEFAULT_PASS']
rabbitmq_port = os.environ['RABBITMQ_DEFAULT_PORT']

mongodb_user = os.environ['MONGO_INITDB_ROOT_USERNAME']
mongodb_pass = os.environ['MONGO_INITDB_ROOT_PASSWORD']
mongodb_port = os.environ['MONGODB_PORT']


broker_url = f'amqp://{rabbitmq_user}:{rabbitmq_pass}@rabbitmq:{rabbitmq_port}'
backend_url = 'rpc://'

celery_app = Celery(
    'celery_app',
    broker=broker_url,
    backend = backend_url
    
)

mongo_db = motor.motor_asyncio.AsyncIOMotorClient('mongo',
                            username=mongodb_user,
                            password=mongodb_pass,
                            )

db = mongo_db['CodeTesting']
submissions = db['Submissions']

# nest_asyncio.apply()

loop = asyncio.get_event_loop()


async def do_update(payload):
    return db.submissions.update_one(payload)


@celery_app.task(name='processPython')
def procesPython(code_id,code_lines):


    logging.info(" [x] Received {}, {}".format(code_id,code_lines) )

    logging.info("Checking for entry in mongo")

    entry = None

    

    with open(f'{code_id}.py','w') as codefile:
        codefile.writelines(code_lines)

    logfile = open('log.txt','w')
    errfile = open('err.txt','w')
    ret = subprocess.run(['python3', f'{code_id}.py'],stdout=logfile,stderr=errfile)


    if ret.returncode == 0:
        with open('log.txt','r') as log:
            exec_output = log.read()

    else:
        with open('err.txt','r') as err:
            exec_output = err.read()

    exec_params = {
        'retcode'     : ret.returncode,  
        'exec_output' : exec_output
    }

    logging.info(" [x] Sending return params to mongo : {}".format(exec_params) )

    try:
        query_task = loop.create_task(do_update({'id' : code_id},{"$set":{'execution':exec_params}}))
        queryres = loop.run_until_complete(query_task)
        logging.info(f"Execution output written : {entry}")
    except:
        logging.error("Could not write entry")

    return exec_params
