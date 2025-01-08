from pymongo import MongoClient

client = MongoClient("localhost", 27018)  # special port mapping, don't get confused
db = client["jumo"]
