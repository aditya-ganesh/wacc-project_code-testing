import streamlit as st
import subprocess
import io
import logging
import pika


creds = pika.credentials.PlainCredentials(username='waccproject',password='waccpassword')




uploaded_file = st.file_uploader("Choose a Python script file",accept_multiple_files=False)

filename_placeholder = st.empty()
code_placeholder = st.empty()
exec_status = st.empty()
exec_output = st.empty()

retval = None

if uploaded_file is not None:

    filename_placeholder.title(uploaded_file.name)
    code_lines = uploaded_file.read()
    code_lines = code_lines.decode("utf-8")
    code_placeholder.code(code_lines,language='python')

    with open('code.py','w') as codefile:
        codefile.writelines(code_lines)

    logfile = open('log.txt','w')
    errfile = open('err.txt','w')
    ret = subprocess.run(['python3', 'code.py'],stdout=logfile,stderr=errfile)


    if ret.returncode == 0:

        exec_status = st.success("Code executed successfully")
        with open('log.txt','r') as log:
            logs = log.read()
            exec_output.success(logs)


    else:

        exec_status = st.error("Code execution failed")
        with open('err.txt','r') as err:
            err = err.read()
            exec_output.error(err)

    try:
        parameters = pika.ConnectionParameters('rabbitmq',5672,'/',creds)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='frontend-stream')
        channel.basic_publish(  exchange='',
                                routing_key='routing_key',
                                body= 'Hello!')
        connection.close()

    except:
        st.exception("RabbitMQ not up yet.")
