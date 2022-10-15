import subprocess
import logging
import time
import json
import os

from pymongo import MongoClient

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

num_cases = 5

celery_app = Celery(
    'celery_app',
    broker=broker_url,
    backend = backend_url
    
)

def connectToMongo():
    mongo_db = MongoClient('mongo',
                                username=mongodb_user,
                                password=mongodb_pass,
                                )
    return mongo_db


@celery_app.task(name='createDBEntry')
def createDBEntry(code_id,filename,code_lines):

    test_cases = {}
    
    for i in range(num_cases):
        test_cases[f'test case {i}'] = {'status' : 'not_started'}

    db_insert = {
        'filename'      :       filename,
        'id'            :       code_id,
        'data'          :       code_lines,
        'execution'     :       test_cases
    }
    mongo_db = connectToMongo()

    db = mongo_db['CodeTesting']
    submissions = db['Submissions']
    try:
        logging.info(f"Writing entry {code_id} to mongo")
        db.submissions.insert_one(db_insert)
    except:
        logging.error(f"Could not create entry : {code_id}")
    return



@celery_app.task(name='testRunner')
def testRunner(code_id,filename,code_lines):

    logging.info(" [x] Received main task : {}".format(code_id) )

    createDBEntry.delay(code_id, filename, code_lines)

    codefile = f'{code_id}.py' 
    with open(codefile,'w') as codefile:
        codefile.writelines(code_lines)
    codefile.close()

    for i in range(num_cases):
        testCase.delay(code_id,i,i)

    return

@celery_app.task(name='testCase')
def testCase(code_id,index,expected):
    
    logging.info(" [x] Received subtask {}, {}".format(code_id,index) )

    codefile = f'{code_id}.py'
    logfile = f'{code_id}_{index}_log.txt'
    errfile = f'{code_id}_{index}_err.txt'
 
    logwriter = open(logfile,'w')
    errwriter = open(errfile,'w')

    ret = subprocess.run(['python3',codefile],stdout=logwriter,stderr=errwriter)

    logwriter.close()
    errwriter.close()

    if ret.returncode == 0:
        with open(logfile,'r') as log:
            exec_output = log.read()
            vartype = type(expected)
            exec_output = vartype(exec_output)

    else:
        with open(errfile,'r') as err:
            exec_output = err.read()

    exec_params = {
        'status'            : 'successful',
        'retcode'           : ret.returncode,  
        'exec_output'       : exec_output,
        'expected_output'   : expected 
    }

    if exec_output != expected:
        exec_params['status'] = 'mismatch'

    os.remove(logfile) 
    os.remove(errfile) 

    logging.info(" [x] Sending return params to mongo : {}".format(exec_params) )

    try:
        mongo_db = connectToMongo()
        db = mongo_db['CodeTesting']
        submissions = db['Submissions']

        update = {f'execution.test case {index}' : exec_params}

        db.submissions.update_one({'id' : code_id},{"$set":update})
        logging.info(f"Execution output written : {entry}")
        mongo_db.close()
    except:
        logging.error("Could not write entry")

    return





@celery_app.task(name='processPython')
def procesPython(code_id,code_lines):


    logging.info(" [x] Received {}, {}".format(code_id,code_lines) )


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
        mongo_db = connectToMongo()
        db = mongo_db['CodeTesting']
        submissions = db['Submissions']
        db.submissions.update_one({'id' : code_id},{"$set":{'execution':exec_params}})
        logging.info(f"Execution output written : {entry}")
        mongo_db.close()
    except:
        logging.error("Could not write entry")

    return exec_params
