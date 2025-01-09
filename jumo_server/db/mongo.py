from pymongo import AsyncMongoClient 

client = AsyncMongoClient("localhost", 27018)  # special port mapping, don't get confused
db = client["jumo"]
