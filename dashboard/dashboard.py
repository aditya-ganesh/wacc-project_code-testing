import streamlit as st
import logging
import time
import json
import requests
import os
import asyncio
import subprocess
from datetime import datetime

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

service_stats = {
    'web1'                  : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'web2'                  : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'rabbitmq'              : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'mongodb-primary'       : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'mongodb-secondary'     : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'mongodb-arbiter'       : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'apiserv'               : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'testcaller'            : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'testrunner'            : {'last_down' : "Never", 'events' : 0,'currently_down' : False},
    'dbhandler'             : {'last_down' : "Never", 'events' : 0,'currently_down' : False},

    }

async def ping_service(service):
    global service_stats
    ret = subprocess.run(["ping", "-c", "1", service])
    if ret.returncode != 0:
        if not service_stats[service]['currently_down']:
            service_stats[service]['currently_down'] = True
            service_stats[service]['last_down'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            service_stats[service]['events'] +=1
    else:
        service_stats[service]['currently_down'] = False


    return ret.returncode

async def show_dashboard():
    global service_stats
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
                stat.write(f"Last down : **{service_stats[service]['last_down']}**")
                stat.write(f"Outage Events : **{service_stats[service]['events']}**")

        time.sleep(2)



async def main():

    title_placeholder.title("Service Dashboard")
    await show_dashboard()


if __name__ == '__main__':
    asyncio.run(main())
