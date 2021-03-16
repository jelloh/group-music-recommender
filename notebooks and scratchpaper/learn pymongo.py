import pymongo
from pymongo import MongoClient


# info to connect to the cluster
# client = pymongo.MongoClient("mongodb+srv://" + USERNAME + ":<" + PASSWORD + 
#                             ">@cluster0.moqmm.mongodb.net" + DATABASE +
#                             "?retryWrites=true&w=majority")
client = pymongo.MongoClient("mongodb+srv://USERNAME:PASSWORD@cluster0.moqmm.mongodb.net/DATABASENAME?retryWrites=true&w=majority")

# connect to our database, which was just named "discord" since idk
db = client["DATABASE NAME"]

# connect to connection
collection = db["COLLECTION NAME"]

# how to add something
# within insert_one({...}) is a "post"
# a "post" is basically just a single entry
# each "post" has an "_id"
# for the user ratings collection, the _id will just be the users discord id
#post = {"_id": 12341234, "name": "aileen"}
#collection.insert_one(post)

# insert many
post1 = {"_id": 11234234, "name": "aileen"}
post2 = {"_id": 12323514, "name": "chanchal"}
post3 = {"_id": 12345234, "name": "austin"}

collection.insert_many([post2, post3])

# find stuff
results = collection.find({"name":"chanchal"})
#print(results)
for result in results:
    print(result["name"], "'s id is ", result["_id"])

# returns the first result
collection.find_one({query})

# delete
results = collection.delete_one({"_id":0})

results = collecition.delete_many({"name": "boop"})

# this would actually just delete everything
results = collection.delete_many({})

# update
results = collection.update_one({"_id": 5}, {"$set" : {"name":"tim"}})
# see documentation for the different command things like $set

# count how many items/rows we have. can also add a specific criteria.
# right now, empty {} just means everything
post_count = collection.count_documents({})

