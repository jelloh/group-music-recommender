class User:
    _id = ""
    ratings = []

    def __init__(self, *args):
        """
        User constructor.
        args[0] --> user id
        """
        if len(args) > 0:
            self._id = args[0]


    def add_rating(self, video_id, rating):
        """
        Add a new video rating for this user.
        """
        r = Rating(video_id, rating)

        if r in self.ratings:
            raise Exception("This video is already rated for this user")

        self.ratings.append(r)

    def __eq__(self, other):
        return self._id == other._id

    def __str__(self):
        ratings = ''

        # this is so ugly im sorry. there is definitely a better way to do this
        for r in self.ratings:
            ratings = ratings + r.__str__() + ', '

        return "{_id: " + self._id + ", ratings: [" + ratings + "]}"


class Rating:
    LIKE = 1
    DISLIKE = -1

    video_id = ""
    rating = 0

    def __init__(self, *args):
        """
        Rating constructor.
        args[0] --> video_id, the idea of the video we are rating
        args[1] --> rating, can either be 1 for LIKE or -1 for DISLIKE. defaults to value 0
        """
        self.rating = 0

        if len(args) > 1:
            rating = args[1]

            if rating != 1 and rating != -1:
                raise AttributeError("Rating is an incorrect value. Can only be 1 (like) or -1 (dislike)")
        
            self.rating = rating
            
        if len(args) > 0:
            self.video_id = args[0]
       
    def set_rating(rating):
        """
        Update this video's rating
        """
        if rating != 1 and rating != -1:
            raise Exception("Rating is an incorrect value. Can only be 1 (like) or -1 (dislike)")

        self.rating = rating

    def clear_rating():
        """
        Clear this video's rating. Though not sure if we will use this ever.
        """
        self.rating = 0

    def __eq__(self, other):
        return self.video_id == other.video_id

    def __str__(self):
        return "{video_id: " + str(self.video_id) + ", rating: " + str(self.rating) + "}"

