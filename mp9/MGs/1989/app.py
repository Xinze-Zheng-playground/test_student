import requests
import time
import json
from flask import Flask, jsonify, redirect, render_template, request
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=34000)
NORTH = 0b1000
EAST = 0b0100
SOUTH = 0b0010
WEST = 0b0001

op = [[-1, 0], [1, 0], [0, 1], [0, -1]]
data = [['0000040', '0000260', '0004000', '0004000', '0004000', '0004000', '0004000'], ['4000000', '4220000', '0040000', '0040000', '0040000', '0040000', '0040000'], [
    '0000000', '0000000', '0000000', '0220220', '0404220', '0400260', '0000000'], ['0000004', '0000004', '0000004', '0202024', '5646464', '1646064', '2222226']]


@ app.route('/')
def start():
    response = requests.put('http://127.0.0.1:5000/addMG', json={"name": "generator1",
                                                                 "url": "http://127.0.0.1:34000/",
                                                                 "author": "Xinze Zheng",
                                                                 "weight": 1})
    print(response.content)
    return 'Add request send', 200


@ app.route('/generate', methods=["GET"])
def StaticMG():
    l = request.json['main']
    idx = 0
    free = []
    free_list = request.json['free']
    while idx < len(free_list):
        free.append([free_list[idx], free_list[idx + 1]])
        idx += 2
    x = l[0]
    y = l[1]
    print(free_list)
    print(free)
    for i in range(x-1, x+1):
        for j in range(y-1, y+1):
            if [i, j] in free and [i+1, j] in free and [i, j+1] in free and [i+1, j+1] in free:
                main = []
                extern = dict()
                for ii in range(i, i+2):
                    for jj in range(j, j+2):
                        if ii == x and jj == y:
                            main = data[(ii-i)*2+(jj-j)]
                        else:
                            extern[f'{int(ii)}_{int(jj)}'] = {
                                'geom': data[(ii-i)*2+(jj-j)]}

                res = {'geom': main, "extern": extern}
                print(res)
                return jsonify(res), 200
    # l = ['0000000','0220220','0404220','0400260','0000000','0000000','0000000']

    l = ['0402400', '4020200', '4004000',
         '4006000', '4060000', '4600000', '0000000']
    res = {'geom': l}
    return jsonify(res), 200
