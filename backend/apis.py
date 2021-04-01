from flask import Flask, Response, request
import pymongo
import json

from user import User, Rating

## ===============================================================================
## Connect to Database
## ===============================================================================

# Get the database password
PASSWORD = ""
with open("../MongoDB Password.txt") as f:
    for line in f:
        PASSWORD = line

app = Flask(__name__)

try:
    mongo = pymongo.MongoClient("mongodb+srv://admin:" + PASSWORD + "@cluster0.moqmm.mongodb.net/database?retryWrites=true&w=majority",
                    serverSelectionTimeoutMS = 1000) #timeout lets us catch the exception

    db = mongo.discord # connect to our database named "discord"

    mongo.server_info() # trigger exception if we can't connect to the database
except:
    print("ERROR - Cannot connect to db")

## ===============================================================================
## User and Rating APIS
## ===============================================================================

@app.route("/ratings", methods = ["POST"])
def create_user():
    try:
        # create a new user based on the inputted id
        user_id = request.form["discord_id"]
        #user = User(user_id)
        user = {
            "_id": request.form["discord_id"],
            "ratings": []
        }

        dbResponse = db.ratings.insert_one(user)

        return Response(
            response = json.dumps(
                {"message": "User successfully created.",
                "id":f"{dbResponse.inserted_id}"
                }
            ),
            status = 200,
            mimetype = "application/json"
        )

    except Exception as ex:
        print(ex)

# Reference:
# https://api.mongodb.com/python/2.9/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_update
@app.route("/ratings/add/<user_id>", methods = ["PATCH"])
def rate_video(user_id):
    """
    user_id - enter the user's id who is rating a video

    @TODO
    We have this set BUT...
    1. We need it to update an existing video if the rating changes rather than just adding a new one
    2. If video exists and the rating is the same, we are done (don't just add another row)
    """
    LIKE = 1
    DISLIKE = -1

    try:
        # get info from API call
        video_id = request.form["video_id"]
        rating = request.form["rating"]

        # create rating 
        #rating = Rating(video_id, rating)
        new_rating = {
            "_id": video_id,
            "rating": int(rating)
        }

        # @TODO if user doesn't exist yet, add them


        # check if current rating already exists @TODO make sure to properly test this
        video_exists = db.ratings.find(
                {"$and":
                [{"_id":user_id},
                {"ratings._id": video_id}]}
            ).count() > 0

        # if not, add the new video and rating
        if(video_exists == False):
            dbResponse = db.ratings.update(
                {"_id": user_id},
                {'$addToSet' : {'ratings': new_rating}}
            )

            return Response(
                response = json.dumps(
                    {"message": "New rating added."}
                ),
                status = 200,
                mimetype = "application/json"
            )

        # if it does, simply update the rating
        else:
            # @TODO update the value instead of just not doing anything



            return Response(
                response = json.dumps(
                    {"message": "Video already exists. No rating added."}
                ),
                status = 200,
                mimetype = "application/json"
            )

    except Exception as ex:
        print(ex)



## ===============================================================================
## beep boop
## ===============================================================================

if __name__ == "__main__":
    app.run(port=80, debug=True)
