from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import uvicorn

import logging
import os

import random
import string

from celery import Celery
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

class codeSubmission(BaseModel):
    submission    : str
    filename      : str
    data          : str       




rabbitmq_user = os.environ['RABBITMQ_DEFAULT_USER']
rabbitmq_pass = os.environ['RABBITMQ_DEFAULT_PASS']
rabbitmq_port = os.environ['RABBITMQ_DEFAULT_PORT']

mongodb_user = os.environ['MONGO_INITDB_ROOT_USERNAME']
mongodb_pass = os.environ['MONGO_INITDB_ROOT_PASSWORD']
mongodb_port = os.environ['MONGODB_PORT']

code_len = int(os.environ['REFCODE_LENGTH'])




mongo_db = MongoClient('mongo',
                            username=mongodb_user,
                            password=mongodb_pass,
                            )

db = mongo_db['CodeTesting']
submissions = db['Submissions']

broker_url = f'amqp://{rabbitmq_user}:{rabbitmq_pass}@rabbitmq:{rabbitmq_port}'
backend_url = 'rpc://'

celery_app = Celery(
                    'celery_app',
                    broker=broker_url,
                    backend = backend_url)
    



 


api_app = FastAPI()



@api_app.get("/")
async def root():
    return {"message": "Hello World"}



@api_app.post("/sendfile")
def send_file(submission: codeSubmission):
    logging.info(submission)

    code_id = ''.join(random.choices(string.ascii_uppercase,k=code_len))
    logging.warning(f'Submission code : {code_id}')

    return_params = {
        'status'    :   0,
        "filename"  :   submission.filename,
        "id"        :   code_id
    }

    db_insert = {
        'filename'      :       submission.filename,
        'id'            :       code_id,
        'data'          :       submission.data
    }


    logging.info("Sending task to celery")
    try:
        task = celery_app.send_task('testRunner', (code_id,submission.filename,submission.data))
    except:
        logging.error("Sending to celery failed")
        return_params['status'] = -1

    return return_params




@api_app.get("/getstatus/{code_id}")
def get_status(code_id):
    entry = {
        'status' : -1
    }
    logging.info(f"Reading mongo for entry {code_id}")
    try:
        queryres = db.submissions.find_one({'id' : code_id})
        logging.info(f"Retrieved : {queryres}")

        entry = {
            'status'        : 0,
            'filename'      : queryres['filename'],
            'code_id'       : queryres['id'],
            'code_lines'    : queryres['data'],
            'execution'     : queryres['execution']
        }

    except:
        logging.error("Reading from mongo failed")

    return entry
