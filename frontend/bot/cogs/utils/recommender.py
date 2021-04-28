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
        self.searched_ids = self.scraper.search_videos(keywords)
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
            
            recommended.append(self.searched_ids[num])
            
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
        
    def view_youtube_list(self):
        print(self.searched_ids)
        
    # --------------------------------------
        
        