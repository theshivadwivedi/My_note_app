from pymongo import MongoClient
MONGODB_URI = "mongodb+srv://shiva:shiva333666@cluster0.yrymvfe.mongodb.net/shiva?retryWrites=true&w=majority"

conn = MongoClient(MONGODB_URI)
db = conn["shiva"]  # database
users_collection = db["users"]
