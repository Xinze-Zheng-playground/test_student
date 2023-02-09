import threading
import requests
import time
import numpy as np


class ServerThread(threading.Thread):
    isRunning = True
    maxChanges = 10
    meanWaitTime = 4
    normalSD = 1
    timeMaxDifference = 2

    def __init__(self, url, name, author, board, status=True):
        threading.Thread.__init__(self)
        self.board = board
        self.status = status
        self.name = name
        self.author = author
        self.url = url
        self.cv = threading.Condition()
        self.statusCode = 200  # assuem it's good
        self.isRunning = True
        self.killed = False

    def run(self):
        while self.killed == False:
            # If staus is not 200, block locally
            while self.status == False or self.isRunning == False:
                try:
                    self.cv.acquire()
                    self.cv.wait()
                finally:
                    self.cv.release()

            if self.killed:
                break

            try:
                response = requests.get(self.url + '/getChange')
            except:
                self.status = False
                self.statusCode = '503'  # Fail to connect with backend
                continue

            self.statusCode = response.status_code
            # Error occurs
            if int(self.statusCode) / 100 != 2:
                self.status = False
                continue

            changes = response.json()["changes"]
            for i in range(min(ServerThread.maxChanges, len(changes))):
                try:
                    x = int(changes[i][0])
                    y = int(changes[i][1])
                    self.board[x][y] = changes[i][2]
                except:
                    continue

            # Generate wait time
            waitTime = np.random.normal(
                ServerThread.meanWaitTime, ServerThread.normalSD)

            lower = ServerThread.meanWaitTime - ServerThread.timeMaxDifference
            upper = ServerThread.meanWaitTime + ServerThread.timeMaxDifference
            if waitTime < lower:
                waitTime = lower
            if waitTime > upper:
                waitTime = upper
            print(f"{self.name}:{waitTime}")
            time.sleep(waitTime)

    def restart(self):
        self.status = True
        self.statusCode = 200
        try:
            self.cv.acquire()
            self.cv.notify()
        finally:
            self.cv.release()

    def pause(self):
        self.isRunning = False

    def resume(self):
        self.isRunning = True
        try:
            self.cv.acquire()
            self.cv.notify()
        finally:
            self.cv.release()

    def kill(self):
        self.killed = True
        self.restart()
