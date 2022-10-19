from celery_common.tasks import databaseHandlerTask
from celery_common.utils import create_worker_from, connectToMongo

import logging
logging.basicConfig(level=logging.INFO)

from pymongo import MongoClient



class databaseHandlerTaskImpl(databaseHandlerTask):

    def run(self, payload):

        code_id = payload['id']
        filename = payload['filename']
        assignment = payload['assignment']
        code_lines = payload['code_lines']

        mongo_db = connectToMongo()
        db = mongo_db['CodeTesting']
        submissions = db['Submissions']
        test_case_coll = db['TestCases']


        logging.info("Getting test cases")

        test_cases_status = {}

   
        preset_test_cases = db.test_cases.find_one({'assignment': assignment})

        logging.info(f"Found : {preset_test_cases}")
        
        if preset_test_cases is not None:
            preset_test_cases = preset_test_cases['test_cases']


            for i in range(len(preset_test_cases)):
                test_cases_status[f'test case {i+1}'] = {
                    'status' : 'not_started',
                    'inputs' : preset_test_cases[f'test case {i+1}']['inputs'] ,  
                    'expected_output' : preset_test_cases[f'test case {i+1}']['outputs']
                }



        payload = {
            'filename'      :       filename,
            'id'            :       code_id,
            'assignment'    :       assignment,
            'data'          :       code_lines,
            'execution'     :       test_cases_status
        }

        logging.info(f"Updating entry to : {payload}")

        try:
            logging.info(f"Writing entry {code_id} to mongo")
            res = db.submissions.find_one({'id' : code_id})
            logging.info("Found entry, replacing")
            res = db.submissions.replace_one({'_id' : res['_id']}, payload)
        except:
            logging.error(f"Could not create entry : {code_id}")

        return payload


# create celery app
app, _ = create_worker_from(databaseHandlerTaskImpl)

# start worker
if __name__ == '__main__':
    app.worker_main()