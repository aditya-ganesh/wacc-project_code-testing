import subprocess
import logging
import time
import pika
import json

creds = pika.credentials.PlainCredentials(username='waccproject',password='waccpassword')
parameters = pika.ConnectionParameters('rabbitmq',5672,'/',creds)

def connect_to_rabbitmq():
    connected = False
    connection = None
    while not connected:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue='frontend-stream')
            connected = True
        except:
            logging.warning("Waiting to connect to RabbitMQ")
            time.sleep(2)
    return channel


def process_frontend_message(ch,method,properties,body):
    logging.warning(" [x] Received %r" % body)

    code_lines = body
    code_lines = code_lines.decode("utf-8")

    with open('code.py','w') as codefile:
        codefile.writelines(code_lines)

    logfile = open('log.txt','w')
    errfile = open('err.txt','w')
    ret = subprocess.run(['python3', 'code.py'],stdout=logfile,stderr=errfile)


    if ret.returncode == 0:
        exec_status = "Code executed successfully"
        with open('log.txt','r') as log:
            exec_output = log.read()


    else:
        exec_status = "Code execution failed"
        with open('err.txt','r') as err:
            exec_output = err.read()

    exec_params = {
        'retcode'     : ret.returncode,  
        'exec_status' : exec_status,
        'exec_output' : exec_output
    }

    channel.basic_publish(  exchange='',
                            routing_key='backend-response',
                            body= json.dumps(exec_params))


def process_events(channel):
    if channel is not None:
        channel.basic_consume(      queue='frontend-stream',
                                    auto_ack=True,
                                    on_message_callback=process_frontend_message)
        logging.warning(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    return

if __name__ == '__main__':
    channel = connect_to_rabbitmq()
    while(True):
        logging.warning("Backend alive")
        process_events(channel)
