from scraper import Scraper
import random

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
    # --------------------------------------    
    
    def recommend(self, K = 1):
        """
        params:
        K - number of videos to return (will return top-K recommendations)

        return:
        a list of video IDs
        """
        if(self.strategy == 0):
            return self.strat_random(K)
            
    
    def change_strategy(self, strat):
        self.strategy = strat
    
    # --------------------------------------
    # RECOMMENDATION STRATEGIES (Individual)
    # --------------------------------------
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
    
    def strat_cos_sim(self, K):
        pass
    
    # --------------------------------------
    # RECOMMENDATION STRATEGIES (Group)
    # --------------------------------------
    def group_least_misery():
        pass
    
    # --------------------------------------
    # OTHER/SUPPORTING METHODS
    # --------------------------------------
    
    def set_strategy(self, num):
        self.strategy = num
    
    def set_keywords(self, keys):
        self.keywords = keys
        
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
        
        