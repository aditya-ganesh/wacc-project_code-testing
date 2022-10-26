from pymongo import MongoClient
import os
import logging
import time
import requests

api_port       = os.environ['APISERV_PORT']


addition_cases = {
   'test case 1' : {'inputs' : [1,2], 'outputs' : 3 },
   'test case 2' : {'inputs' : [3,0], 'outputs' : 3 },
   'test case 3' : {'inputs' : [-12.5,5], 'outputs' : -7.5 }
}
addition = {
   'assignment' : 'addition',
   'test_cases' : addition_cases
}

strrev_cases = {
   'test case 1' : {'inputs' : 'ABCDE', 'outputs' : 'EDCBA' },
   'test case 2' : {'inputs' : 'The Rain in Spain', 'outputs' : 'niapS ni niaR ehT' },
}
strrev = {
   'assignment' : 'string reversal',
   'test_cases' : strrev_cases
}

payload={
   1 : addition,
   2 : strrev
   }



def initTestCaseCollection(payload):
   res = requests.post(url=f'http://apiserv:{api_port}/sendfile',json=payload)


def verifyWrite():
   res = requests.get(url=f'http://apiserv:{api_port}/getassignments')
   logging.warning(f"Received : {res.json()}")

if __name__ == '__main__':
   initTestCaseCollection(payload)
   verifyWrite()



