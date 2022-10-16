print("Check if something is happening")

db = conn.getDB("CodeTesting");

db.createCollection("TestCases");

db.TestCases.insertOne([
 {
    "assignment": "addition",
    "test_cases": 
    {
        "test case 1" : {"inputs" : [1,2], "outputs" : 3 },
        "test case 2" : {"inputs" : [3,0], "outputs" : 3 },
        "test case 3" : {"inputs" : [-12.5,5], "outputs" : -7.5 }
    }
  }
]);