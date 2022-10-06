import streamlit as st
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

celery_app = None

title = st.title("Code Tester")
uploaded_file = st.file_uploader("Choose a Python script file",accept_multiple_files=False)

filename_placeholder = st.empty()
code_placeholder = st.empty()
wait_placeholder = st.empty()
exec_status = st.empty()
exec_output = st.empty()




def connect_to_rabbitmq():

    global celery_app

    while celery_app is None:
        try:
                celery_app = Celery(
                    'celery_app',
                    broker=broker_url,
                    backend = backend_url   )
        except:
            logging.info("Waiting to connect to RabbitMQ")
            time.sleep(2)



def update_placeholders(payload):

    global exec_status, exec_output

    logging.info("Received : {}".format(payload))

    ret = payload['retcode']

    wait_placeholder = st.empty()

    if ret == 0:
        exec_status.success(payload['exec_status'])
        exec_output.success(payload['exec_output'])
    else:
        exec_status.error(payload['exec_status'])
        exec_output.error(payload['exec_output'])



def get_execution_response(task):

    global celery_app

    if celery_app is not None:
        logging.info("Getting task results")
        payload = task.get()
        update_placeholders(payload)


def process_input():

    global celery_app

    if uploaded_file is not None:

        filename_placeholder.header(uploaded_file.name)
        code_lines = uploaded_file.read()
        code_lines = code_lines.decode("utf-8")
        code_placeholder.code(code_lines,language='python')

        code_id = 'code'

        logging.info("Sending task to celery")
        task = celery_app.send_task('processPython', (code_id,code_lines))

        # wait_placeholder.spinner("Waiting for execution output")
        
        get_execution_response(task)


if __name__ == '__main__':

    connect_to_rabbitmq()
    if celery_app is not None:
        process_input()
