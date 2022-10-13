from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import uvicorn

import logging
import os

import random
import string

from celery import Celery
import motor
import tornado
import tornado.web
import nest_asyncio


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

# tornado_port = os.environ['TORNADO_PORT']


code_len = int(os.environ['REFCODE_LENGTH'])




mongo_db = motor.motor_tornado.MotorClient('mongo',
                            username=mongodb_user,
                            password=mongodb_pass,
                            )

db = mongo_db['CodeTesting']
submissions = db['Submissions']

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        db = self.settings['db']

tornado_app = tornado.web.Application([
    (r'/', MainHandler)
], db=db)

nest_asyncio.apply()

# using env tornado_port resulted in a key error
tornado_app.listen(8888)
tornado.ioloop.IOLoop.current().start()

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


async def do_insert(document):
    return await db.submissions.insert_one(document)

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


    
    logging.info("Adding submission to mongo")
    try:
        tornado.ioloop.IOLoop.current().run_sync(do_insert(db_insert))
    except:
        logging.error("Adding to mongo failed")
        return_params['status'] = -1

    logging.info("Sending task to celery")
    try:
        task = celery_app.send_task('processPython', (code_id,submission.data))
    except:
        logging.error("Sending to celery failed")
        return_params['status'] = -2

    return return_params


async def do_find(code_id):
    return await db.submissions.find_one({'id' : code_id})


@api_app.get("/getstatus/{code_id}")
def get_status(code_id):
    entry = {
        'status' : -1
    }
    logging.info(f"Reading mongo for entry {code_id}")
    try:
        queryres = tornado.ioloop.IOLoop.current().run_sync(do_find(code_id))
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
