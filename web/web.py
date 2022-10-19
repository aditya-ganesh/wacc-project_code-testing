import streamlit as st
import logging
import time
import json
import requests
import os

api_port = os.environ['APISERV_PORT']

title_placeholder = st.empty()


def upload_submission():

    assignments = requests.get(url=f'http://apiserv:{api_port}/getassignments/')
    assignments = assignments.json()

    
    assignment_code = st.selectbox("Choose an assignment",assignments)
    uploaded_file = st.file_uploader("Choose a Python script file",accept_multiple_files=False)
 
    if uploaded_file is not None:

        code_lines = uploaded_file.read()
        code_lines = code_lines.decode("utf-8")

        st.header(uploaded_file.name)
        st.code(code_lines,language='python')

        payload = {
            'assignment'    : assignment_code,
            'filename'      : uploaded_file.name,
            'data'          : code_lines             
        }

        try:

            res = requests.post(url=f'http://apiserv:{api_port}/sendfile',json=payload)

            if res.ok:

                ret = res.json()

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

        st.write(res)

        if res is not None:

            st.header('{} - {}'.format(res['id'],res['filename']))
            st.code(res['data'])

            if 'execution' in res.keys():
                test_results = res['execution']
                for i in range(len(test_results)):

                    result = test_results[f'test case {i+1}']
                    if result['status'] != 'not_started':
                        if result['retcode'] == 0:
                            if result['status'] == 'successful':
                                st.success(f"Case {i} : Passed\nExpected : {result['expected_output']}\tGot : {result['exec_output']}")
                            else:
                                st.warning(f"Case {i} : Failed\nExpected : {result['expected_output']}\tGot : {result['exec_output']}")
                        else:
                            st.error(f'Case {i} : Execution failed. Traceback below')
                            st.error(res['exec_output'])
                    else:
                        st.info(f"Case {i} : Pending execution")


        # if res['status'] == 0:
        #     st.header('{} - {}'.format(res['code_id'],res['filename']))
        #     st.code(res['code_lines'],language='python')

        #     test_results = res['execution']

        #     for i in range(len(test_results)):

        #         result = test_results[f'test case {i+1}']
        #         if result['status'] != 'not_started':
        #             if result['retcode'] == 0:
        #                 if result['status'] == 'successful':
        #                     st.success(f"Case {i} : Passed\nExpected : {result['expected_output']}\tGot : {result['exec_output']}")
        #                 else:
        #                     st.warning(f"Case {i} : Failed\nExpected : {result['expected_output']}\tGot : {result['exec_output']}")
        #             else:
        #                 st.error(f'Case {i} : Execution failed. Traceback below')
        #                 st.error(res['exec_output'])
        #         else:
        #             st.info(f"Case {i} : Pending execution")


if __name__ == '__main__':

        title_placeholder.title("Code Testing Platform")

        sitepages = {
            "Upload a submission" : upload_submission,
            "View a result" : view_result
        }

        page_selection = st.sidebar.selectbox("I want to...",sitepages.keys())
        sitepages[page_selection]()
