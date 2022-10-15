import motor.motor_asyncio

def create_db():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = "mongodb+srv://admin:ZIDA6eai8UbEn0gz@cluster0.rftianv.mongodb.net/test"
 
   client = motor.motor_asyncio.AsyncIOMotorClient(CONNECTION_STRING) 

   return client['user_shopping_list']
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
   # Get the database
   dbname = create_db()