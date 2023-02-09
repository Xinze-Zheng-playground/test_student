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

dictionary = {
    0: ['4c', '46'],
    1: ['04', '04'],
    2: ['0e', '42'],
    3: ['0e', '06'],
    4: ['46', '04'],
    5: ['4a', '06'],
    6: ['4a', '46'],
    7: ['0c', '04'],
    8: ['4e', '46'],
    9: ['4e', '06']
}

# starting coordinates


@ app.route('/')
def start():
    response = requests.put('http://127.0.0.1:5000/addMG', json={"name": "fun-dynamic",
                                                                 "url": "http://127.0.0.1:34001/",
                                                                 "author": "Xinze ZHeng",
                                                                 "weight": 1})
    print(response.content)
    return 'Add request send', 200


@ app.route('/generate', methods=["GET"])
def fun():
    response = ['0000000', '0000000', '0000000',
                '0000000', '0000000', '0000000', '0000000']
    l = request.json['main']

    x = l[0]
    y = l[1]
    if (x > 999 or y > 999 or x < -99 or y < -99):
        response = ['0222200', '4002400', '4046400',
                    '4002600', '4040000', '4040000', '4040000']
        res = {'geom': response}
        return jsonify(res), 200

    if (x < 0):
        x = abs(x)
        l1 = '02' + dictionary[int(x %
                                   100 / 10)][0] + dictionary[int(x % 10)][0] + '00'
        l2 = '00' + dictionary[int(x %
                                   100 / 10)][1] + dictionary[int(x % 10)][1] + '00'
    else:
        l1 = dictionary[int(x / 100)][0] + dictionary[int(x %
                                                      100 / 10)][0] + dictionary[int(x % 10)][0] + '00'
        l2 = dictionary[int(x / 100)][1] + dictionary[int(x %
                                                      100 / 10)][1] + dictionary[int(x % 10)][1] + '00'
    if (y < 0):
        y = abs(y)
        l4 = '02' + dictionary[int(y %
                                   100 / 10)][0] + dictionary[int(y % 10)][0] + '00'
        l5 = '00' + dictionary[int(y %
                                   100 / 10)][1] + dictionary[int(y % 10)][1] + '00'
    else:
        l4 = dictionary[int(y / 100)][0] + dictionary[int(y %
                                                      100 / 10)][0] + dictionary[int(y % 10)][0] + '00'
        l5 = dictionary[int(y / 100)][1] + dictionary[int(y %
                                                      100 / 10)][1] + dictionary[int(y % 10)][1] + '00'
    response[1] = l1
    response[2] = l2
    response[4] = l4
    response[5] = l5

    res = {'geom': response}
    return jsonify(res), 200
