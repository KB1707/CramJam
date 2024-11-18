from pymongo import MongoClient

class UsersDB:
    def __init__(self):
        # Replace with your MongoDB connection string
        self.client = MongoClient("mongodb+srv://sushwetabm:Y3f26QzxsDyap7E9@cluster0.afhog.mongodb.net/cram-jam-db")
        self.db = self.client["cram_jam_db"]
        self.users_collection = self.db["users"]

    def find_user(self, username, password):
        return self.users_collection.find_one({"user": username, "password": password})

    def add_user(self, username, password):
        if self.users_collection.find_one({"user": username}):
            return False  # User already exists
        self.users_collection.insert_one({"user": username, "password": password})
        return True
