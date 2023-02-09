from pixelation import pixelation
import numpy as np
import time
import requests
import sys
from flask import jsonify
url = 'http://127.0.0.1:5000/'
starting_row = 0
starting_col = 0
board_width = 50
board_height = 50
picture_width = 20
picture_height = 20
id = 0
pixel_rate = 1  # ms
picture = list()
palette = list()


def init():
    print('----Initialize----')
    global url
    global id
    global board_height
    global board_width
    global picture
    global palette

    info = dict()
    info['name'] = 'PG'
    info['author'] = 'Xinze-Zheng'
    info['secret'] = '1234569'
    response = requests.put(
        url=url + 'register-pg', json=info)

    if response.status_code == 200:
        print("Registered successfully")
        id = response.json()['id']
        print(f'id = {id}')
    else:
        print("Registeration failed")
        return False

    response = requests.get(url + "settings")
    if response.status_code != 200:
        print("Fetch setting fails")
        return False

    palette = list(response.json()['palette'])
    picture = pixelation('ghost.png', picture_width, picture_height, palette)
    print('Picture generated')
    return True


def update():
    global id
    global url
    global pixel_rate

    while True:
        board = requests.get(url=url + "pixels",
                             json={'id': id}).json()['pixels']
        flag = False
        for i in range(picture_height):
            for j in range(picture_width):
                if (board[starting_row + i][starting_col + j] != picture[i][j]):
                    tmp = dict()
                    tmp['id'] = id
                    tmp['row'] = starting_row + i
                    tmp['col'] = starting_col + j
                    tmp['color'] = picture[i][j]
                    response = requests.put(
                        url=url + '/update-pixel', json=tmp)
                    if response.status_code != 200:
                        print(response.status_code)
                        print(response.content)
                    else:
                        pixel_rate = response.json()['rate']
                    flag = True
                    break
            if flag:
                break

        time.sleep(pixel_rate / 1000 + 0.1)
        print(f'pixel-rate: {pixel_rate}')


if init():
    update()
