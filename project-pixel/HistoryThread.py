import threading
import time
from ServerDB import ServerDB


class HistoryThread(threading.Thread):

    def __init__(self, board, db: ServerDB, interval=10):
        threading.Thread.__init__(self)
        self.interval = interval
        self.isRunning = True
        self.killed = False
        self.db = db
        self.board = board
        self.cv = threading.Condition()

    def run(self):
        print("Start thread")
        while self.killed == False:

            while self.isRunning == False:
                try:
                    self.cv.acquire()
                    self.cv.wait()
                finally:
                    self.cv.release()

            if self.killed:
                break

            self.db.addHistory(board=self.board)
            time.sleep(10)

    '''Pause the recorder'''

    def pause(self):
        self.isRunning = False

    '''Resume recording histories'''

    def resume(self):
        self.isRunning = True
        try:
            self.cv.acquire()
            self.cv.notify()
        finally:
            self.cv.release()

    '''Kill the recorder'''

    def kill(self):
        self.killed = True
        self.resume()
