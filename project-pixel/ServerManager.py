from ServerDB import ServerDB
from ServerThread import ServerThread
import numpy as np
import requests
from HistoryThread import HistoryThread
''' Class that provide interface for routes'''


class ServerManager:
    def __init__(self, board, loadDB):
        self.DB = ServerDB()
        self.servers = {}  # Internal caches for the servers
        self.displays = {}
        self.board = board
        self.recorder = HistoryThread(board=self.board, db=self.DB)
        if loadDB:
            self.load()
        else:
            self.DB.removeAll()

    '''Interact with DB and load the stored servers'''

    def load(self):
        for server in self.servers.items():
            server.stop()

        self.servers = {}
        all_servers = self.DB.get_all_servers()
        print(f"{len(all_servers)} stored servers")
        for server in all_servers:
            thread = ServerThread(
                server['url'], server['name'], server['author'], self.board)
            self.servers[server['_id']] = thread
            thread.start()

        print(self.servers)

    '''Add server, servers are considered identical if they have same name and author'''

    def addServer(self, data: dict):
        resId = ''
        storedServer = (self.DB.get_server(
            name=data['name'], author=data['author']))
        if storedServer == None:

            result = self.DB.add_server(data)
            if result:
                data['_id'] = str(data['_id'])  # store database ID
                thread = ServerThread(
                    data['url'], data['name'], data['author'], self.board)
                self.servers[data['_id']] = thread  # map id to thread
                thread.start()
                resId = data['_id']
        else:
            id = storedServer['_id']
            self.DB.update_server(id=id, data=data)
            server = self.servers[id]
            server.url = data['url']
            resId = None
            if server.status == False:
                server.restart()

        return resId

    '''Restart a server of given id'''

    def restartServer(self, id):
        if id in self.servers.keys():
            self.servers[id].restart()
            return "Restart request sent", 200
        else:
            return "Id does not exist", 200

    '''Restart all servers no matter connection issue or is paused'''

    def restartAll(self):
        for key in self.servers.keys():
            self.servers[key].restart()
            self.servers[key].resume()

    '''Pause a particular given the id'''

    def pauseServer(self, id):
        if id in self.servers.keys():
            self.servers[id].pause()
            return "Pause successful", 201
        else:
            return "Server not exist", 400

    '''Pause all threads from running'''

    def pauseAll(self):
        for server in self.servers.values():
            server.pause()

    '''Resume a server from given id, will not resume if previous status is not 200'''

    def resumeServer(self, id):
        if id in self.servers.keys():
            self.servers[id].resume()
            return "Resume successfully", 200
        else:
            return "Id not exists", 400

    '''Resume all servers, servers with error in status will not resume'''

    def resumeAll(self):
        for server in self.servers.values():
            server.resume()

    '''Remove server from DB and caches, stop the thread'''

    def removeServer(self, id):
        if id in self.servers.keys():
            if self.DB.remove_server(id=id):
                self.servers[id].kill()
                del self.servers[id]
                return f"{id} is successfully deleted", 200
            else:
                return "Fail to delete from DB", 401
        else:
            return "Server not found", 400

    '''Display the server by calling url/display'''

    def displayServer(self, id):
        board = None
        if id not in self.servers.keys():
            return 404
        server = self.servers[id]
        response = requests.get(server.url + '/display')
        if response.status_code != 200 or board not in response.json().keys():
            return response.status_code

        self.displays[id] = response.json['board']
        return 200

    '''Clear the whole DB and caches'''

    def clearDB(self):
        for server in self.servers.values():
            server.kill()
        self.servers = {}
        self.DB.removeAll()

    '''Start recording of History, should be called only once'''

    def StartRecordHistory(self):
        print("start thread")
        self.recorder.start()

    '''Return states of the board in time order'''

    def getHistory(self):
        l = self.DB.getHistory()
        serverList = sorted(l, key=lambda e: e['board'])
        return serverList

    '''Delete the history DB'''

    def deleteHistories(self):
        self.DB.removeHistory()
        return "Delete Success", 200

    def pauseRecording(self):
        self.recorder.pause()
        return "Pause Success", 200

    def resumeRecording(self):
        self.recorder.resume()
        return "Resume Success", 200
