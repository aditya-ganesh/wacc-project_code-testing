from celery_common.tasks import testRunnerTask
from celery_common.utils import create_worker_from, connectToMongo

import subprocess
import os
import json
import time

import logging
logging.basicConfig(level=logging.INFO)

class testRunnerTaskImpl(testRunnerTask):

    def run(self, payload):
        """ actual implementation """

        

        code_id = payload['id']
        code_lines = payload['code_lines']
        index = payload['index']

        logging.info(f"Test runner received : ID - {code_id}, index - {index}, payload {payload}")

        code_filename = f'{code_id}_{index}.py'
        with open(code_filename,'w') as codefile:
            codefile.writelines(code_lines)
            codefile.close()


        logfile = f'{code_id}_{index}_log.txt'
        errfile = f'{code_id}_{index}_err.txt'
    
        logwriter = open(logfile,'w')
        errwriter = open(errfile,'w')

        process_call = ['python3',code_filename]

        inputs = payload['test_case']['inputs']
        exp_outputs = payload['test_case']['outputs']

        print(f"Using inputs : {inputs}")

        logging.info(f"Number of inputs : {len(inputs)}")
        logging.info(f"Type of input : {type(inputs)}")

        if type(inputs) == str:
            process_call.append(inputs)
        else:
            for input in inputs:
                process_call.append(str(input))

        
        logging.info(f"Starting execution : {process_call}")

        ret = subprocess.run(process_call,stdout=logwriter,stderr=errwriter)

        logwriter.close()
        errwriter.close()

        

        if ret.returncode == 0:
            with open(logfile,'r') as log:
                exec_output = log.read()

                if type(exp_outputs) in [int, float]:
                    exec_output = float(exec_output)
                elif type(exp_outputs) == str:
                    exec_output = exec_output[:-1]

        else:
            with open(errfile,'r') as err:
                exec_output = err.read()

        exec_params = {
            'status'            : 'successful',
            'retcode'           : ret.returncode,  
            'exec_output'       : exec_output,
            'inputs'            : inputs,  
            'expected_output'          : exp_outputs
        }


        if exec_output != exp_outputs :
            exec_params['status'] = 'mismatch'
        if ret.returncode != 0:
            exec_params['status'] = 'failed'

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



        os.remove(code_filename)
        os.remove(logfile) 
        os.remove(errfile) 

        return 


# create celery app
app, _ = create_worker_from(testRunnerTaskImpl)

# start worker
if __name__ == '__main__':
    app.worker_main()
