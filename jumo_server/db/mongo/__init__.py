from pymongo import AsyncMongoClient

from jumo_server.consts import TEST_MODE

db_name = "jumo_test" if TEST_MODE else "jumo"

client = AsyncMongoClient(
    "localhost", 27018
)  # special port mapping, don't get confused
db = client[db_name]
