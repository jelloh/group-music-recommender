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
2. Navigate to our project's cluster and click "Connect"
3. Click "Connect using MongoDB Compass" and copy the connection string
4. Within MongoDB Compass, click "New Connection" and paste the connection string
5. Replace "password" in the string with our actual password and click connect

