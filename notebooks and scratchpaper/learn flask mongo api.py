from flask import Flask, Response, request
import pymongo
import json

# we may not need this. is to work with ObjectId
# (which is like the default id mongodb gives things?)
from bson.objectid import ObjectId

app = Flask(__name__)

try:
    mongo = pymongo.MongoClient("mongodb+srv://admin:boopityboopboop7!@cluster0.moqmm.mongodb.net/database?retryWrites=true&w=majority",
                    serverSelectionTimeoutMS = 1000) #timeout lets us catch the exception

    db = mongo.company # connect to our database named "company" in this case (for example)

    mongo.server_info() # trigger exception if we can't connect to the database
except:
    print("ERROR - Cannot connect to db")


## ----------------------------------------------------

@app.route("/users/<id>", methods=["PATCH"])
def update_user(id):
    try:
        # note we use ObjectId here... in our own work, we probably don't need this
        # if we are using the users' discord id's as the id (since it wont be an ObjectId in that case)
        dbResponse = db.users.update_one(
            {"_id": ObjectId(id)},
            {"$set":{"name":request.form["name"]}}
        )

        # for attr in dir(dbResponse):
        #     print(f"*****{attr}******")
        if dbResponse.modified_count == 1:
            return Response(
                response=  json.dumps(
                    {"message":"user updated"}),
                status = 200, 
                mimetype="application/json"
            )
        else:
            return Response(
                response=  json.dumps(
                    {"message":"nothing to update"}),
                status = 200, 
                mimetype="application/json"
            )

    except Exception as ex:
        print("**********")
        print(ex)
        print("**********")
        return Response(
            response=  json.dumps(
                {"message":"sorry cannot update user"}),
            status = 500, # 500 for error
            mimetype="application/json"
        )



## ----------------------------------------------------

@app.route("/users", methods=["GET"])
def get_some_users():
    try:
        data = list(db.users.find())
        
        for user in data:
            # confert the fancy object id to just a text id
            user["_id"] = str(user["_id"])

        return Response(
            response = json.dumps(
                data),
            status = 500,
            mimetype="application/json"
        )

    except Exception as ex:
        print(ex)
        return Response(
            response=  json.dumps(
                {"message":"cannot read users"}),
            status = 500, # 500 for error
            mimetype="application/json"
        )


## ----------------------------------------------------

@app.route("/users", methods = ["POST"])
def create_user():
    try:
        user = {
            "name": request.form["name"], 
            "lastName": request.form["lastName"]}
        # db.users is the collection named "users" (change later)
        dbResponse = db.users.insert_one(user)
        # for attr in dir(dbResponse):
        #     print(attr)
        #print(dbResponse.inserted_id)

        return Response(
            response=  json.dumps(
                {"message":"user created", 
                "id":f"{dbResponse.inserted_id}"
                }),
            status=200,
            mimetype="application/json"
        )


    except Exception as ex:
        print("***********")
        print(ex)
        print("***********")

## ----------------------------------------------------

if __name__ == "__main__":
    app.run(port=80, debug=True)