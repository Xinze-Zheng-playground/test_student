import random
import requests
import time
import json
from flask import Flask, jsonify, redirect, render_template, request
from dotenv import load_dotenv
import numpy as np

load_dotenv()
app = Flask(__name__)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=34000)
NORTH = 0b1000
EAST = 0b0100
SOUTH = 0b0010
WEST = 0b0001
NUM_ROWS = 7
NUM_COLS = 7

# starting coordinates


@ app.route('/')
def start():
    response = requests.put('http://127.0.0.1:5000/addMG', json={"name": "xinze-dynamic",
                                                                 "url": "http://127.0.0.1:34001/",
                                                                 "author": "Your Name",
                                                                 "weight": 1})
    print(response.content)
    return 'Add request send', 200


# @ app.route('/generate', methods=["GET"])
def StaticMG():
    l = ['0222200', '4002400', '4046400',
         '4002600', '4040000', '4040000', '4040000']
    res = {'geom': l}
    return jsonify(res), 200


@ app.route('/generate', methods=["GET"])
def dfs():
    M = np.zeros((NUM_ROWS, NUM_COLS, 5), dtype=np.uint8)
    starts = [[0, 3], [6, 3], [3, 0], [3, 6]]
    choice = random.choice(starts)
    r = choice[0]
    c = choice[1]
    history = [(r, c)]
    while history:
        M[r, c, 4] = 1
        check = []
        if c > 0 and M[r, c - 1, 4] == 0:
            check.append('L')
        if c < NUM_COLS - 1 and M[r, c + 1, 4] == 0:
            check.append('R')
        if r < NUM_COLS - 1 and M[r + 1, c, 4] == 0:
            check.append('D')
        if r > 0 and M[r - 1, c, 4] == 0:
            check.append('U')

        if len(check):
            history.append([r, c])
            move_direction = random.choice(check)

            if move_direction == 'L':
                M[r, c, 0] = 1
                c = c - 1
                M[r, c, 2] = 1
            if move_direction == 'R':
                M[r, c, 2] = 1
                c = c + 1
                M[r, c, 0] = 1
            if move_direction == 'U':
                M[r, c, 1] = 1
                r = r - 1
                M[r, c, 3] = 1
            if move_direction == 'D':
                M[r, c, 3] = 1
                r = r + 1
                M[r, c, 1] = 1
        else:
            r, c = history.pop()

    image = np.zeros((NUM_ROWS, NUM_COLS))
    for row in range(0, NUM_ROWS):
        for col in range(0, NUM_COLS):
            cell = M[row, col]
            #L is blocked
            if M[row, col, 0] == 0:
                image[row, col] += WEST
            #U is blocked
            if M[row, col, 1] == 0:
                image[row, col] += NORTH
            if M[row, col, 2] == 0:
                image[row, col] += EAST
            if M[row, col, 3] == 0:
                image[row, col] += SOUTH
    for end in starts:
        image[end[0], end[1]] = 0
    result = list()
    for i in range(0, NUM_ROWS):
        s = ''
        for j in range(0, NUM_COLS):
            s += f'{int(image[i][j]):x}'
        result.append(s)

    res = {'geom': result}
    print(result)
    return jsonify(res), 200
