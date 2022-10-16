from pymongo import MongoClient
import os


mongodb_user = os.environ['MONGO_INITDB_ROOT_USERNAME']
mongodb_pass = os.environ['MONGO_INITDB_ROOT_PASSWORD']
mongodb_port = os.environ['MONGODB_PORT']
drop_existing = os.environ['DROP_EXISTING']


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

def connectToMongo():
    mongo_db = MongoClient('mongo',
                                username=mongodb_user,
                                password=mongodb_pass,
                                )
    return mongo_db


def initTestCaseCollection():
   mongo_db = connectToMongo()
   
   db = mongo_db['CodeTesting']
   test_cases = db['TestCases']
   submissions = db['Submissions']

   if drop_existing:
      test_cases.drop()
      submissions.drop()


   db.test_cases.insert_one(addition)
   db.test_cases.insert_one(strrev)

   mongo_db.close()

if __name__ == '__main__':
   initTestCaseCollection()