import datetime


class FrontendManager:
    secondInterval = 3

    def __init__(self, board) -> None:
        self.frontends = {}
        self.board = board
        self.validIds = []
        self.loadNetId()

    def loadNetId(self):
        '''TODO, load a document of valid id'''

    '''Check if netid is valid, and if the frontend update too frequently, if legal action, updateboard'''

    def updateChange(self, id, x, y, color):
        '''TODO: Check if netid is valid and check the timestamp for this netid'''
        if id not in self.frontends.keys():
            self.frontends[id] = datetime.datetime.now()
            self.board[int(x) // 2][int(y) // 2] = int(color)
            return "Success", 200

        else:
            if self.frontends[id] + datetime.timedelta(0, FrontendManager.secondInterval) < datetime.datetime.now():
                self.frontends[id] = datetime.datetime.now()
                self.board[int(x) // 2][int(y) // 2] = int(color)
                return "Success", 200
            else:
                return "Too freqeunt update", 400
