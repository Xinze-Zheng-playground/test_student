from pixelation import pixelation
import numpy as np
import time
import requests
import sys
from flask import jsonify
url = 'http://fa22-cs340-109.cs.illinois.edu:3340/'
starting_row = 37
starting_col = 0
board_width = 100
board_height = 50
picture_width = 5
picture_height = 5
id = 0
pixel_rate = 1  # ms
picture = list()
palette = list()
background = list()

def init():
    print('----Initialize----')
    global url
    global id
    global board_height
    global board_width
    global picture
    global palette
    global background

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
    picture = pixelation('dinosaurs.png', picture_width, picture_height, palette)
    background = pixelation('bg.png', board_width, board_height, palette)
    print(background)
    print('Picture generated')
    return True


def update():
    global id
    global url
    global pixel_rate
    global starting_col
    global starting_row
    global background
    while True:
        board = requests.get(url=url + "pixels",
                             json={'id': id}).json()['pixels']
        flag = False
        not_change = True
        for i in range(picture_height):
            for j in range(picture_width):
                if (picture[i][j] != -1 and board[starting_row + i][starting_col + j] != picture[i][j]):
                    tmp = dict()
                    tmp['id'] = id
                    tmp['row'] = starting_row + i
                    tmp['col'] = starting_col + j
                    tmp['color'] = picture[i][j]
                    not_change = False
                    print(tmp)
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

        time.sleep(pixel_rate / 1000)

        if not_change:
            time.sleep(0.1)
            starting_col = (starting_col + 5) % (board_width)
            if starting_col > 40 and starting_col < 80:
                starting_row = max(30 - int(((starting_col - 45) // 1.5)), 30 - int(((80 - starting_col) // 1.5)))
            else:
                starting_row = 37
            board = requests.get(url=url + "pixels",
                                json={'id': id}).json()['pixels']
            for i in range(board_height):
                for j in range(board_width):
                    if (background[i][j] != -1 and board[i][j] != background[i][j]):
                        tmp = dict()
                        tmp['id'] = id
                        tmp['row'] = i
                        tmp['col'] = j
                        tmp['color'] = background[i][j]

                        response = requests.put(
                            url=url + '/update-pixel', json=tmp)
                        if response.status_code != 200:
                            print(response.status_code)
                            print(response.content)
                        else:
                            pixel_rate = response.json()['rate']
                
        

if init():
    update()
