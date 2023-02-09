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
    l = ['0220220', '4004220', '4220260',
         '0200020', '0646440', '0604460', '0000000']
    res = {'geom': l}
    return jsonify(res), 200
