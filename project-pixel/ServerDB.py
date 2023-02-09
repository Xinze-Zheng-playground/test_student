from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
HOST = 'localhost'
PORT = 27017
DB_NAME = 'cs340-PGs'
HISTORY_NAME = 'cs340-histories'
server_keys = ['name', 'url', 'author']


class ServerDB:
    def __init__(self, host=HOST, port=PORT, db_name=DB_NAME):
        self.mongo = MongoClient(host, port)
        self.db = self.mongo[DB_NAME]
        self.history = self.mongo[HISTORY_NAME]

    def __del__(self):
        if self.mongo:
            self.mongo.close()

    def stringify_id(document):
        document["_id"] = str(document["_id"])
        return document

    def add_server(self, data):
        return self.db.servers.insert_one(data)

    def update_server(self, id, data):
        return self.db.servers.update_one({"_id": ObjectId(id)}, {"$set": data})

    def remove_server(self, id):
        return self.db.servers.delete_one({"_id": ObjectId(id)})

    def get_server(self, name, author):
        found = self.db.servers.find_one({"name": name, "author": author})

        if found:
            found = ServerDB.stringify_id(found)
            return found

        return None

    def get_all_servers(self):
        result = self.db.servers.find({})

        if result:
            result = list(result)
            for server in result:
                server = ServerDB.stringify_id(server)
            return result

        return []

    def removeAll(self):
        print(self.db.name)
        self.mongo.drop_database(DB_NAME)
        return None

    def removeHistory(self):
        self.mongo.drop_database(HISTORY_NAME)
        return None

    def addHistory(self, board):
        data = {'board': board, 'time': datetime.datetime.now().timestamp()}
        self.history.history.insert_one(data)
        print("Add history")

    def getHistory(self):
        result = self.history.history.find({})

        if result:
            result = list(result)
            for server in result:
                server = ServerDB.stringify_id(server)
            return result

        return []
