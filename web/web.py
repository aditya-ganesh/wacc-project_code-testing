import streamlit as st
import logging
import time
import json
import requests
import os
import asyncio

api_port = os.environ['APISERV_PORT']

title_placeholder = st.empty()


async def upload_submission():

    assignment_code = None
    uploaded_file = None

    # uploaded_file = st.file_uploader("Choose a Python script file",accept_multiple_files=False)
    #
    # try:
    #     assignments = await requests.get(url=f'http://apiserv:{api_port}/getassignments/')
    #     assignments = assignments.json()
    #     assignment_code = st.selectbox("Choose an assignment",assignments)
    # except:
    #     st.warning("A connection to the database could not be established. You can still view the code you upload, but it will not be processed. Please try again later.")
    #     logging.warning("Could not fetch assignments")

    with st.form("CodeSubmission"):
        uploaded_file = st.file_uploader("Choose a Python script file",accept_multiple_files=False)

        assignment_container = st.empty()
        assignment_container.info("Fetching list of assignments from the database")

        try:
            assignments = requests.get(url=f'http://apiserv:{api_port}/getassignments/',timeout=3)
            assignments = assignments.json()
            assignment_code = assignment_container.selectbox("Choose an assignment",assignments)
        except:
            assignment_container.warning("A connection to the database could not be established. You can still view the code you upload, but it will not be processed. Please try again later.")
            logging.warning("Could not fetch assignments")

        submitted = st.form_submit_button("Submit")
 
    if uploaded_file is not None and submitted:

        code_lines = uploaded_file.read()
        code_lines = code_lines.decode("utf-8")

        st.header(uploaded_file.name)
        st.code(code_lines,language='python')

        payload = {
            'assignment'    : assignment_code,
            'filename'      : uploaded_file.name,
            'data'          : code_lines
        }


        if assignment_code is not None:

            res = requests.post(url=f'http://apiserv:{api_port}/sendfile',json=payload)

            if res.ok:

                ret = res.json()

                if ret['status'] == 0:

                    st.success(f"File uploaded! Your reference ID is **{ret['id']}**")

                    st.header("Test Case Execution")
                    await print_test_cases(ret['id'])

                else:
                    st.error(f"Something went wrong, please try again.\nError code : {ret['status']}")







async def print_test_cases(code_id):


    test_containers = []
    found = False
    test_cases_received = False

    while not test_cases_received:

        logging.info(f"Trying to read test cases for {code_id}")

        try:
            res = requests.get(url=f'http://apiserv:{api_port}/getstatus/{code_id}')
            res = res.json()
            found = True
        except:
            st.error("Could not fetch test cases. Please try again later")
        # Get number of test cases to create placeholder values

        if found and 'execution' in res.keys():
            test_results = res['execution']
            if len(test_results) > 0:
                test_cases_received = True
                for i in range(len(test_results)):
                    test_containers.append(st.empty())
        else:
            await asyncio.sleep(1)
        
    pending_count = [1 for i in range(len(test_results))]

    while test_cases_received and sum(pending_count) > 0:

        try:
            res = requests.get(url=f'http://apiserv:{api_port}/getstatus/{code_id}')
            res = res.json()
        except:
            st.error("Could not fetch test cases. Please try again later")
            break

        if 'execution' in res.keys():
            test_results = res['execution']
            for i in range(len(test_results)):
                result = test_results[f'test case {i+1}']
                if result['status'] == 'queued':
                    test_containers[i].info(f"Case {i} : Queued")
                elif result['status'] == 'timeout' :
                    test_containers[i].error(f"Case {i} : Timed out.")
                    pending_count[i] = 0
                else:
                    if result['retcode'] == 0:
                        if result['status'] == 'successful':
                            test_containers[i].success(f"Case {i} : Passed\nExpected : {result['expected_output']}\tGot : {result['exec_output']}")
                        else:
                            test_containers[i].warning(f"Case {i} : Failed\nExpected : {result['expected_output']}\tGot : {result['exec_output']}")
                    else:
                        test_containers[i].error(f"Case {i} : Execution failed : {result['exec_output']}")
                    pending_count[i] = 0
        
        await asyncio.sleep(2)

    return


async def view_result():

    code_id = st.text_input("Enter your reference ID")
    if code_id != "":
        res = requests.get(url=f'http://apiserv:{api_port}/getstatus/{code_id}')
        res = res.json()


        if res is not None:

            st.header('{} - {}'.format(res['id'],res['filename']))
            st.code(res['data'])

            await print_test_cases(code_id)




async def main():

    title_placeholder.title("Code Testing Platform")

    sitepages = {
        "Upload a submission" : upload_submission,
        "View a result" : view_result
    }

    page_selection = st.sidebar.selectbox("I want to...",list(sitepages.keys()))
    await sitepages[page_selection]()


if __name__ == '__main__':
    asyncio.run(main())
