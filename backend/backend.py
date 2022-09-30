import subprocess
import logging
import time
import pika

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


def callback(ch,method,properties,body):
    logging.warning(" [x] Received %r" % body)

def process_events(channel):
    if channel is not None:
        channel.basic_consume(      queue='frontend-stream',
                                    auto_ack=True,
                                    on_message_callback=callback)
        logging.warning(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    return

if __name__ == '__main__':
    channel = connect_to_rabbitmq()
    while(True):
        logging.warning("Backend alive")
        process_events(channel)
