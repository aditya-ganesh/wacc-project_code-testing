#!/bin/bash


MONGODB1=mongo1
MONGODB2=mongo2
MONGODB3=mongo3

echo "Starting replica set initialize"
until mongosh --host mongo1 --eval "print(\"waited for connection\")"
do
    sleep 2
done
echo "Connection finished"
echo "Creating replica set"
mongosh --host mongo1 <<EOF
config = {
    "_id" : "rs",
    "members" : [
        {
            "_id" : 0,
            "host" : "mongo1:27017"
        },
        {
            "_id" : 1,
            "host" : "mongo2:27018"
        },
        {
            "_id" : 2,
            "host" : "mongo3:27019"
        }
    ]
  }
  rs.initiate(config);
EOF
echo "Replica set created"

mongosh <<EOF
   use admin;
   admin = db.getSiblingDB("admin");
   admin.createUser(
     {
	user: "$MONGO_INITDB_ROOT_USERNAME",
        pwd: "$MONGO_INITDB_ROOT_PASSWORD",
        roles: [ { role: "root", db: "admin" } ]
     });
     db.getSiblingDB("admin").auth("$MONGO_INITDB_ROOT_USERNAME", "$MONGO_INITDB_ROOT_PASSWORD");
     rs.status();
EOF



# echo "Calling Replica set initialisation"

# mongosh <<EOF
#    var cfg = {
#         "_id": "rs",
#         "version": 1,
#         "members": [
#             {
#                 "_id": 0,
#                 "host": "mongo1:27017",
#                 "priority": 2
#             },
#             {
#                 "_id": 1,
#                 "host": "mongo2:27017",
#                 "priority": 0
#             },
#             {
#                 "_id": 2,
#                 "host": "mongo3:27017",
#                 "priority": 0
#             }
#         ]
#     };
#     rs.initiate(cfg, { force: true });
#     //rs.reconfig(cfg, { force: true });
#     rs.status();
# EOF

# sleep 10

# echo "Creating admin user"

# mongosh <<EOF
#    use admin;
#    admin = db.getSiblingDB("admin");
#    admin.createUser(
#      {
# 	user: "$MONGO_INITDB_ROOT_USERNAME",
#         pwd: "$MONGO_INITDB_ROOT_PASSWORD",
#         roles: [ { role: "root", db: "admin" } ]
#      });
#      db.getSiblingDB("admin").auth("$MONGO_INITDB_ROOT_USERNAME", "$MONGO_INITDB_ROOT_PASSWORD");
#      rs.status();
# EOF

