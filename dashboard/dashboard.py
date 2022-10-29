import streamlit as st
import logging
import time
import json
import requests
import os
import asyncio
import subprocess


title_placeholder = st.empty()

service_placeholders = {

    'web1'                  : st.empty(),
    'web2'                  : st.empty(),
    'rabbitmq'              : st.empty(),
    'mongodb-primary'       : st.empty(),
    'mongodb-secondary'     : st.empty(),
    'mongodb-arbiter'       : st.empty(),
    'apiserv'               : st.empty(),
    'testcaller'            : st.empty(),
    'testrunner'            : st.empty(),
    'dbhandler'             : st.empty(),


    }

async def ping_service(service):
    ret = subprocess.run(["ping", "-c", "1", service])
    return ret.returncode

async def show_dashboard():

    while True:
        for service in service_placeholders:
            retval = await ping_service(service)
            with service_placeholders[service]:
                serv,stat = st.columns(2)
                serv.write(service)
                if retval == 0:
                    stat.success("OK")
                else:
                    stat.error("Fail")

        time.sleep(2)



async def main():

    title_placeholder.title("Service Dashboard")
    await show_dashboard()


if __name__ == '__main__':
    asyncio.run(main())
