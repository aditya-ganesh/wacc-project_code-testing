from fastapi import FastAPI, File, UploadFile, Body, Request
from pydantic import BaseModel
import uvicorn

import logging
import os

import random
import string

from celery_common.tasks import testCallerTask, databaseHandlerTask
from celery_common.utils import create_worker_from, connectToMongo

from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

class codeSubmission(BaseModel):
    assignment    : str
    filename      : str
    data          : str       




rabbitmq_user = os.environ['RABBITMQ_DEFAULT_USER']
rabbitmq_pass = os.environ['RABBITMQ_DEFAULT_PASS']
rabbitmq_port = os.environ['RABBITMQ_DEFAULT_PORT']


code_len = int(os.environ['REFCODE_LENGTH'])




 


api_app = FastAPI()



@api_app.get("/")
async def root():
    return {"message": "Hello World"}


@api_app.get("/getassignments")
async def get_assignments():
    entry = {
        'status' : -1
    }
    logging.info(f"Reading mongo for assignments")
    # try:
    mongo_db = connectToMongo()
    db = mongo_db['CodeTesting']
    test_cases = db['TestCases']
    queryres = db.test_cases.distinct('assignment')
    logging.info(f"Retrieved : {queryres}")
    entry = queryres
    # except:
    #     logging.error("Reading from mongo failed")

    return entry


@api_app.post("/initdb")
def init_database(payload: dict = Body(...)):
    logging.info("Initialising DB from API call")
    mongo_db = connectToMongo()
    db = mongo_db['CodeTesting']
    test_cases = db['TestCases']

    for testcase in payload:
        db.test_cases.insert_one(testcase)


@api_app.post("/sendfile")
def send_file(submission: codeSubmission):
    logging.info(submission)

    code_id = ''.join(random.choices(string.ascii_uppercase,k=code_len))
    logging.warning(f'Submission code : {code_id}')

    return_params = {
        'status'    :   0,
        'assignment'    : submission.assignment,
        'filename'  :   submission.filename,
        'id'        :   code_id
    }

    payload = {
        'id' : code_id,
        'assignment' : submission.assignment,
        'filename'   : submission.filename,
        'code_lines' : submission.data,
    }

    db_insert = {
        'filename'      :       submission.filename,
        'id'            :       code_id,
        'assignment'    :       submission.assignment,
        'data'          :       submission.data
    }

    _, test_caller = create_worker_from(testCallerTask)
    

    logging.info("Creating initial DB entry")
    

    mongo_db = connectToMongo()
    db = mongo_db['CodeTesting']
    submissions = db['Submissions']
    db.submissions.insert_one(db_insert)

    logging.info("Sending test caller task to celery")
    test_caller.apply_async(args=[payload,])




    return return_params


@api_app.get("/getstatus/{code_id}")
def get_status(code_id):
    entry = {
        'status' : -1
    }
    logging.info(f"Reading mongo for entry {code_id}")
   
    mongo_db = connectToMongo()
    db = mongo_db['CodeTesting']
    submissions = db['Submissions']

    queryres = db.submissions.find_one({'id' : code_id})
    if queryres is not None:
        queryres.pop('_id')
    logging.info(f"Retrieved : {queryres}")

    return queryres
