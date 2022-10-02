import streamlit as st
import subprocess
import io
import logging
import pika
import time
import json

creds = pika.credentials.PlainCredentials(username='waccproject',password='waccpassword')
parameters = pika.ConnectionParameters('rabbitmq',5672,'/',creds)


uploaded_file = st.file_uploader("Choose a Python script file",accept_multiple_files=False)

filename_placeholder = st.empty()
code_placeholder = st.empty()
exec_status = st.empty()
exec_output = st.empty()


connection = None
channel = None


def connect_to_rabbitmq():

    global connection, channel

    connected = False
    while not connected:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue='frontend-stream')
            channel.queue_declare(queue='backend-response')
            connected = True
        except:
            logging.warning("Waiting to connect to RabbitMQ")
            time.sleep(2)



def update_placeholders(payload):

    global exec_status, exec_output, connection, channel

    exec_params = json.loads(payload)
    ret = exec_params['retcode']

    if ret == 0:
        exec_status.success(exec_params['exec_status'])
        exec_output.success(exec_params['exec_output'])
    else:
        exec_status.error(exec_params['exec_status'])
        exec_output.error(exec_params['exec_output'])

    channel.close()


def process_backend_message(ch,method,properties,body):
    logging.warning(" [x] Received %r" % body)
    update_placeholders(body)
    


def get_execution_response():

    global connection, channel

    if channel is not None:
        channel.basic_consume(      queue='backend-response',
                                    auto_ack=True,
                                    on_message_callback=process_backend_message)
        logging.warning(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()



def process_input():

    global connection, channel


    retval = None

    if uploaded_file is not None:

        filename_placeholder.title(uploaded_file.name)
        code_lines = uploaded_file.read()
        code_lines = code_lines.decode("utf-8")
        code_placeholder.code(code_lines,language='python')

        channel.basic_publish(  exchange='',
                                routing_key='frontend-stream',
                                body= code_lines)
        
        get_execution_response()


if __name__ == '__main__':

    connect_to_rabbitmq()
    if channel is not None:
        process_input()
    connection.close()
