from scraper import Scraper
import random

class Recommender:
    def __init__(self, keywords):
        """
        To start - we need to have a list of keywords.
        (At least for now, until we add other strategies)
        """
        self.strategy = 0
        self.keywords = keywords
        
        # Before beginning, get the initial list of keywords
        self.scraper = Scraper()
        self.searched_ids = self.scraper.search_videos(self.keywords)
        
        #CHANCE = 0.5 # chance for recommending songs someone has already heard and liked
        self.flag = True # rename this eventually so it makes more sense.
                    # True if we need to collect the video data. False if we have already done that
                    # for this iteration and don't need to do it again.
        
        self.df = None # dataframe for searched songs from keyword list
        self.searched_embeds = None # embeddings generated from searched songs
            # --------------------------------------    
    
    def recommend(self, users = None, K = 1):
        """
        params:
        users = list of users (discord user id). 
                Default is None for strategies that don't require users (e.g., random one)
        K - number of videos to return (will return top-K recommendations)
        
        return:
        a list of video IDs
        """
        if(self.strategy == 0):
            print("Random strategy!")
            return self.strat_random(K)
        elif(self.strategy == 1):
            print("Average without misery strategy")
            return self.average_without_misery(K, users)
    
    def change_strategy(self, strat):
        self.strategy = strat
    
    # --------------------------------------
    # RECOMMENDATION STRATEGIES (Individual)
    # --------------------------------------
    def strat_cos_sim_description_only(self, user_id):
        """
        Input - user_id: The id of a given user.
        Output - A list of videos and their cosine score.
        """
        recommended = []

        # REMINDER: change "ids" to self.searched_ids()
        # self.searched_ids() 

        # Step 1 - Get the data of searched videos
        if self.flag == True:
            print("1. Getting the data")
            self.df = scraper.get_video_data(self.searched_ids)
            #flag = False

        # Step 2 - Get data of user's liked videos
        # Get the url for the api call
        print("2. Get liked video data")
        url = f"http://localhost/ratings/get_ratings/{user_id}"
        # Make the api call
        r = requests.get(url)
        # Get dataframe based on video ids
        ratings = pd.DataFrame(r.json()) # get the id and ratings from the api call
        u_df = scraper.get_video_data(ratings['_id'].values.tolist()) # get the data based on id
        u_df = pd.merge(u_df, ratings, left_on='video_id', right_on='_id') # merge data and ratings

        # Step 3 - Sentence Transformers!
        print("3. Sentence transformers!")
        model = SentenceTransformer('paraphrase-distilroberta-base-v1') # get the model

        # Make embeddings from descriptions. This may take some time.
        if self.flag == True:
            searched_descriptions = list(self.df['description']) 
            self.searched_embeds = model.encode(searched_descriptions, convert_to_tensor=True)
            self.flag = False

        rated_descriptions = list(u_df['description'])
        liked_embeds = model.encode(rated_descriptions, convert_to_tensor=True)

        # Step 4 - Cosine Similarity
        print("4. Calculating cosine similarity")
        cosine_scores = util.pytorch_cos_sim(searched_embeds, liked_embeds).numpy()

        scores = []
        r = [row.rating for row in ratings.itertuples()]
        for i in range(0, len(cosine_scores)):
            index = list(cosine_scores[i]).index(max(cosine_scores[i]))
            #print(index)
            scores.append({'score':max(cosine_scores[i]) * r[index],
                           'video_id':self.df.iloc[i]['video_id']})

        #print(scores.head())
        # return [convert_to_url(i) for i in scores.nlargest(K, ['score'])['video_id']]
        #return scores.nlargest(K, ['score'])
        return scores
    
    # --------------------------------------
    # RECOMMENDATION STRATEGIES (Group)
    # --------------------------------------
    def average_without_misery(self, K, users, threshold = 0):
        """
        Input - 
            K: Number of recommendations (top-k) to return
            users: a list of user ids
            threshold: the threshold for which videos to cut out in average without misery
                       by default, this is 0 (meaning cut out videos similar to any videos a user has disliked)
                       Should be a value between 0 - 1
        Output -
            A list of top-K recommended videos (YouTube URLs returned)
        """
        # get the scores for each user, using individual recommendation methods
        scores = []
        for u in users:
            #print(u)
            scores.append({"user": u, "scores": strat_cos_sim_description_only(u)})

        removed_negatives = []
        # Calculate average without misery. "misery" determined by threshold
        # Iterate through all the searched videos that we are choosing from
        for video_index in range(0, len(self.searched_ids)):  

            negatives = False
            average = 0
            num_users = len(scores) # len(users) would also work

            for user_index in range(0, num_users):
                user = scores[user_index]['user']

                # if the video does not meet the threshold (e.g., is negative and a user disliked it)
                # then do not include it in the final list of videos to recommend
                if(scores[user_index]['scores'][video_index]['score'] < THRESHOLD):
                    negatives = True
                    break
                # else, we take the average
                else:
                    average = average + scores[user_index]['scores'][video_index]['score']

            if negatives == False:
                average = average/num_users
                if(average < 0.999): # dont include those with 1, meaning everyone has already heard it
                    #print(average)
                    removed_negatives.append({"score" : average, "video_id": ids[video_index]})

        # return URLs from top K recommended songs
        return [convert_to_url(i) for i in pd.DataFrame(removed_negatives).nlargest(K, columns=['score'])['video_id']]
    
    def strat_random(self, K):
        recommended = []
        
        for i in range(0, K):
            
            # generate random number (for rand video)
            num = random.randint(0,len(self.searched_ids))
            
            # if random video is already in the list, pick another
            while self.searched_ids[num] in recommended:
                num = random.randint(0,len(self.searched_ids))
            
            recommended.append(self.convert_to_url(self.searched_ids[num]))
            
        return recommended
    # --------------------------------------
    # OTHER/SUPPORTING METHODS
    # --------------------------------------
    
    def set_strategy(self, num):
        self.strategy = num
    
    def set_keywords(self, keys):
        self.keywords = keys
        self.flag = True # set to true since keywords change
        
    def view_keywords(self):
        print(self.keywords)

    def get_keywords(self):
        return self.keywords

    def update_video_list(self):
        self.scraper = Scraper()
        self.searched_ids = self.scraper.search_videos(self.keywords)
        
    def view_youtube_list(self):
        print(self.searched_ids)
        
    def convert_to_url(self, y_id):
        # https://www.youtube.com/watch?v=q3J0H5SAhJY
        return f"https://www.youtube.com/watch?v={y_id}"
        
    # --------------------------------------
        
        