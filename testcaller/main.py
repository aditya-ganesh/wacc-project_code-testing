from celery_common.tasks import testCallerTask, testRunnerTask, databaseHandlerTask
from celery_common.utils import create_worker_from, connectToMongo

import logging
logging.basicConfig(level=logging.INFO)

from pymongo import MongoClient


class testCallerTaskImpl(testCallerTask):

    def run(self, payload):
        """ actual implementation """
        logging.info(f"Test caller received : {payload}")

        
        _, db_handler = create_worker_from(databaseHandlerTask)
        logging.info("Sending db update task to celery")
        db_handler.apply_async(args=[payload,])
        

        mongo_db = connectToMongo()
        db = mongo_db['CodeTesting']
        cases = db['TestCases']
        res =  db.test_cases.find_one({'assignment': payload['assignment']})
        logging.info(f"Found test cases : {res}")
        test_cases = res['test_cases']


        for i in range(len(test_cases)):   
            payload['test_case'] = test_cases[f'test case {i+1}']
            payload['index'] = i+1
            logging.info(f"Sending test case subtask : {payload}")
            _, test_runner = create_worker_from(testRunnerTask)
            test_runner.apply_async([payload,])



        return 


# create celery app
app, _ = create_worker_from(testCallerTaskImpl)

# start worker
if __name__ == '__main__':
    app.worker_main()