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
def createDBEntry(code_id,filename,code_lines,assignment,num_cases=5):

    test_cases = {}
    
    for i in range(num_cases):
        test_cases[f'test case {i+1}'] = {'status' : 'not_started'}

    db_insert = {
        'filename'      :       filename,
        'id'            :       code_id,
        'assignment'    :       assignment,
        'data'          :       code_lines,
        'execution'     :       test_cases
    }
    try:
        mongo_db = connectToMongo()
        db = mongo_db['CodeTesting']
        submissions = db['Submissions']
        test_case_coll = db['TestCases']

        logging.info(f"Writing entry {code_id} to mongo")
        db.submissions.insert_one(db_insert)
    except:
        logging.error(f"Could not create entry : {code_id}")
    return



@celery_app.task(name='testRunner')
def testRunner(code_id,assignment,filename,code_lines):

    logging.info(" [x] Received main task : {}".format(code_id) )

    mongo_db = connectToMongo()
    db = mongo_db['CodeTesting']
    cases = db['TestCases']
    res =  db.test_cases.find_one({'assignment': assignment})
    logging.info(f"Found test cases : {res}")
    test_cases = res['test_cases']

    createDBEntry.delay(code_id, filename, code_lines,assignment,len(test_cases))

    

    codefile = f'{code_id}.py' 
    with open(codefile,'w') as codefile:
        codefile.writelines(code_lines)
    codefile.close()

    # TODO : Change iterator to take each test case

    for i in range(1,len(test_cases)+1):
        case = test_cases[f'test case {i}']
        logging.info(f"Taking test case : {case}")
        testCase.delay(code_id,i,case)

    return

@celery_app.task(name='testCase')
def testCase(code_id,index,test_case):
    
    logging.info(" [x] Received subtask {}, {}".format(code_id,index) )

    codefile = f'{code_id}.py'
    logfile = f'{code_id}_{index}_log.txt'
    errfile = f'{code_id}_{index}_err.txt'
 
    logwriter = open(logfile,'w')
    errwriter = open(errfile,'w')

    process_call = ['python3',codefile]

    print(f"Using inputs : {test_case['inputs']}")

    logging.info(f"Number of inputs : {len(test_case['inputs'])}")
    logging.info(f"Type of input : {type(test_case['inputs'])}")

    if type(test_case['inputs']) == str:
        process_call.append(test_case['inputs'])
    else:
        for input in test_case['inputs']:
            process_call.append(str(input))

    
    logging.info(f"Starting execution : {process_call}")


    ret = subprocess.run(process_call,stdout=logwriter,stderr=errwriter)

    logwriter.close()
    errwriter.close()

    if ret.returncode == 0:
        with open(logfile,'r') as log:
            exec_output = log.read()

            if type(test_case['outputs']) in [int, float]:
                exec_output = float(exec_output)
            elif type(test_case['outputs']) == str:
                exec_output = exec_output[:-1]

    else:
        with open(errfile,'r') as err:
            exec_output = err.read()

    exec_params = {
        'status'            : 'successful',
        'retcode'           : ret.returncode,  
        'exec_output'       : exec_output,
        'expected_output'   : test_case['outputs'] 
    }

    if exec_output != test_case['outputs'] :
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
