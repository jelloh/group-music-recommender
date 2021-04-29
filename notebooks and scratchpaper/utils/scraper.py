# Allows us to connect to the YouTube API service
from googleapiclient.discovery import build
import math
import pandas as pd

# idk what to call this
class Scraper:
    def __init__(self):
        API_KEY = ""

        # Read in the API key
        with open("../YouTube API Key.txt") as f:
            for line in f:
                API_KEY = line

        # Create the service
        self.youtube_service = build('youtube', 'v3', developerKey=API_KEY)

    def search_videos(self, search_terms, pages = 5, results_per_page = 50):
        """
        Search videos on YouTube given a list of various keywords or key phrases.
        Return a list of YouTube video IDs.
        
        search_terms: a list of search terms. each search term will be a new search
        pages: the number of pages we want to retrieve per search (default 5)
        results_per_page: the number of results per page we want to retrieve per search (max is 50)
        returns a list of video ids
        
        """
        
        # initialize empty list to store video ids
        list_of_ids = []
        
        # ID for the video category of music is 10
        MUSIC_CATEGORY_ID = 10

        for search_term in search_terms:
            
            # get the first page of videos for the search term
            request = self.youtube_service.search().list(
                        part='snippet',
                        maxResults=results_per_page,
                        q=search_term,
                        type='video',
                        videoCategoryId = MUSIC_CATEGORY_ID,
                        )
            response = request.execute()

            # iterate through the response and save just the video id's
            for item in response['items']:
                list_of_ids.append(item['id']['videoId'])
                    
            # we already searched once, so get the remaining X-1 pages (where X is number of pages)
            for page in range(1, pages):
                last_request = request
                last_response = response

                request = self.youtube_service.search().list_next(
                                        previous_request = last_request,
                                        previous_response = last_response)
                response = request.execute()
                
                # iterate through the response and save just the video id's
                for item in response['items']:
                    list_of_ids.append(item['id']['videoId'])

        # done!    
        return list_of_ids

    def get_video_data(self, ids):
        """
        Returns a pandas dataframe (for now) of video data.
        
        ids: the list of video ids
        """
        
        # initialize empty dataframe to build off of
        df = pd.DataFrame(columns=['video_id','title','localized_title','description','localized_description',
                            'tags','channel_title','duration','view_count','like_count','dislike_count',
                            'comment_count','topic_categories'])

        for i in range(0, math.ceil(len(ids)/50)):
            
            # 50 is the max items we can get per request
            start = i * 50
            end = (i * 50) + 50
            
            request = self.youtube_service.videos().list(
                part='snippet, contentDetails, statistics, topicDetails',
                id=ids[start:end])

            response = request.execute()
            
            for j in range(0,len(response['items'])):
            
                # get all the different features from the api response
                video_id = response['items'][j]['id']
                title = response['items'][j]['snippet']['title']
                localized_title = response['items'][j]['snippet']['localized']['title']
                description = response['items'][j]['snippet']['description']
                localized_description = response['items'][j]['snippet']['localized']['description']

                try:
                    tags = response['items'][j]['snippet']['tags']
                except:
                    tags = 'none'

                channel_title = response['items'][j]['snippet']['channelTitle']
                duration = response['items'][j]['contentDetails']['duration']
                view_count = response['items'][j]['statistics']['viewCount']
                
                try:
                    like_count = response['items'][j]['statistics']['likeCount']
                except:
                    like_count = -1
                    
                try:
                    dislike_count = response['items'][j]['statistics']['dislikeCount']
                except:
                    dislike_count = -1
                    
                try:
                    comment_count = response['items'][j]['statistics']['commentCount']
                except:
                    comment_count = -1

                try:
                    topic_categories = response['items'][j]['topicDetails']
                except:
                    topic_categories = 'none'

                df = df.append({'video_id':video_id,'title':title,'localized_title':localized_title,
                    'description':description,'localized_description':localized_description,
                    'tags':tags,'channel_title':channel_title,'duration':duration,
                    'view_count':view_count,'like_count':like_count,'dislike_count':dislike_count,
                    'comment_count':comment_count, 'topic_categories':topic_categories}, ignore_index=True) 
        
        return df