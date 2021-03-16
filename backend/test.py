from user import User, Rating

user = User("1234")

user.add_rating("1", Rating.LIKE)
user.add_rating("2", Rating.DISLIKE)
user.add_rating("3", Rating.LIKE)
user.add_rating("3", Rating.LIKE)


print(user)