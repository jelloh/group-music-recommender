# group-music-recommender
Term project for ITIS 6410/8410

## Setup  
1. git clone this repository  
2. install pipenv from [here](https://pipenv.pypa.io/en/latest/) if you don't already have it  
3. run `pipenv install` (this should install all the required libraries)  
4. run `pipenv shell` to go into the newly created environment  
  
### Getting a YouTube API Key 
1. Go to [console.developers.google.com](https://console.cloud.google.com/projectselector2/apis/dashboard?pli=1&supportedpurview=project)  
2. Click **Create Project**
3. Choose a name for your project and click **Create**
4. Click **Enable APIs and Services**
5. Search for the "YouTube" API, and we will use the **YouTube Data API v3**
6. Click **Enable**. We can now create the API key.
7. Click **Create Credentials**
8. Select the API we will be running (YouTube), and that we are running the API from "Other non-UI" (since we are using Python scripts). We will also select that we will be accessing "Public data" (for now at least).
9. Save the API key given!

File will be named "YouTube API Key.txt" and stored in just the main repository.
  
### Setup MongoDB  
1. Install [MongoDB Compass](https://www.mongodb.com/products/compass)  
2. Navigate to our project's cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/lp/try2?utm_source=bing&utm_campaign=bs_americas_united_states_search_brand_atlas_desktop&utm_term=mongodb%20atlas&utm_medium=cpc_paid_search&utm_ad=e&utm_ad_campaign_id=355813668&msclkid=265f839c6b3716819913e3fe4281332f) after signing in and click "Connect"
3. Click "Connect using MongoDB Compass" and copy the connection string
4. Within MongoDB Compass, click "New Connection" and paste the connection string
5. Replace "password" in the string with our actual password and click connect
 
## Backend  
To run the backend, create a text file in the main repository named "MongoDB Password.txt" and paste our MongoDB Atlas cluster password there.  
Then run:  
```
cd backend 
python apis.py
```  

It should now be running! (Make sure you are also in your environment when you do this. If not, run `pipenv shell` first)

## Discord Bot  
To run the discord bot, first run Lavalink:  
```
java -jar jdk-13.0.1\bin\Lavalink.jar
```