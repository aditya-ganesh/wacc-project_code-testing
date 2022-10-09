import streamlit as st
import logging
import time
import json
import requests
import os

api_port = os.environ['APISERV_PORT']


assignments = [1,2]

title_placeholder = st.empty()


def upload_submission():

    submission_code = st.selectbox("Choose an assignment",assignments)
    uploaded_file = st.file_uploader("Choose a Python script file",accept_multiple_files=False)
 
    if uploaded_file is not None:

        code_lines = uploaded_file.read()
        code_lines = code_lines.decode("utf-8")

        st.header(uploaded_file.name)
        st.code(code_lines,language='python')

        payload = {
            'submission'    : submission_code,
            'filename'      : uploaded_file.name,
            'data'          : code_lines             
        }

        st.write(payload)

        try:

            res = requests.post(url=f'http://apiserv:{api_port}/sendfile',json=payload)

            if res.ok:

                ret = res.json()
                st.write(ret)
                if ret['status'] == 0:
                    
                    st.success("File uploaded! Your reference ID is")
                    st.header(ret['id'])
                else:
                    st.error(f"Something went wrong, please try again.\nError code : {ret['status']}")
        except:
            st.error("Something went wrong. Please try again")


def view_result():

    code_id = st.text_input("Enter your reference ID")
    if code_id != "":
        res = requests.get(url=f'http://apiserv:{api_port}/getstatus/{code_id}')
        res = res.json()

        if res['status'] == 0:
            st.header('{} - {}'.format(res['code_id'],res['filename']))
            st.code(res['code_lines'],language='python')

            if res['execution']['retcode'] == 0:
                st.success('No execution errors')
            else:
                st.error('Execution failed. Traceback below')
            st.info(res['execution']['exec_output'])



if __name__ == '__main__':

        title_placeholder.title("Code Testing Platform")

        sitepages = {
            "Upload a submission" : upload_submission,
            "View a result" : view_result
        }

        page_selection = st.sidebar.selectbox("I want to...",sitepages.keys())
        sitepages[page_selection]()