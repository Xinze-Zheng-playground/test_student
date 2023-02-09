

from pixelation import pixelation
import numpy as np
from flask import Flask, jsonify
import time
import requests
import threading
import sys
sys.path.append("../..")
app = Flask(__name__)
board = np.zeros((400, 400), np.unsignedinteger).tolist()
url = 'http://fa22-cs340-adm.cs.illinois.edu:34999/'
target = []
width = 40
height = 40
id = 0


@app.route('/', methods=["GET"])
def start():
    info = dict()
    global url
    info['name'] = 'PG'
    info['author'] = 'Xinze-Zheng'
    info['secret'] = '1234569'
    response = requests.put(
        url=url + 'register-pg', json=info)
    global target
    global height
    global width
    global id
    id = response.json()['id']
    response = requests.get(url + "settings")

    palette = list(response.json()['palette'])

    target = pixelation('William.png', width, height, palette)

    getChange()
    return "OK", 200


def getChange():
    global id
    global url
    timer = requests.get(url + "settings").json()["pixel_rate"]
    while True:
        board = requests.get(url + "pixels").json()['pixels']
        flag = False
        for i in range(height):
            for j in range(width):
                if (board[i][j] != target[i][j]):
                    tmp = dict()
                    tmp['id'] = id
                    tmp['row'] = i
                    tmp['col'] = j
                    tmp['color'] = target[i][j]
                    response = requests.put(
                        url=url + '/update-pixel', json=tmp)
                    flag = True
                    break
            if flag:
                break
        # update pixel rate
        timer = requests.get(
            url+"settings").json()["pixel_rate"]
        time.sleep(timer / 1000 + 0.5)
        print(timer)
