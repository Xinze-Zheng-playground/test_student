from pixelation import pixelation
import numpy as np
import time
import requests
import sys
from flask import jsonify
url = 'http://fa22-cs340-adm.cs.illinois.edu:34000/'
starting_row = 52
starting_col = 141
board_width = 50
board_height = 50
picture_width = 14
picture_height = 14
picture_name = 'bean.png'
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
    info['secret'] = 'PG+eGluemV6Mg==+M0YxQbYkQHsWfefKPM75cRtZaE9E3L'
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
    picture = pixelation(picture_name, picture_width, picture_height, palette)
    print('Picture generated')
    return True


def update():
    global id
    global url
    global pixel_rate

    while True:
        board = requests.get(url = url + "pixels",
                             json={'id': id}).json()['pixels']
        flag = False
        for i in range(picture_height):
            for j in range(picture_width):
                if (picture[i][j] != -1 and board[starting_row + i][starting_col + j] != picture[i][j]):
                    tmp = dict()
                    tmp['id'] = id
                    tmp['row'] = starting_row + i
                    tmp['col'] = starting_col + j
                    tmp['color'] = picture[i][j]
                    print(tmp)
                    check_board = requests.get(url = url + "pixels",
                             json={'id': id}).json()['pixels']
                    if check_board[starting_row + i][starting_col + j] != picture[i][j]:
                        response = requests.put(
                            url=url + '/update-pixel', json=tmp)
                        if response.status_code != 200:
                            print(response.status_code)
                            print(response.content)
                        else:
                            pixel_rate = response.json()['rate']
                            print(pixel_rate)
                        flag = True
                        break
                    else:
                        continue
            if flag:
                break

        time.sleep(pixel_rate / 1000)


if init():
    update()
