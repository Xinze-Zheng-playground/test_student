from flask import Flask, jsonify, render_template, request
import requests
import random
import threading


app = Flask(__name__)
REMOVE_FRM_BOARD = 0

# palette = ["#FFFFFF", "#C0C0C0", "#808080", "#000000", "#5D99B8", "#C73DD5"]


@app.route('/', methods=['GET'])
def changeColor():
    # threading.Timer(5.0, changeColor).start()
    info = dict()
    info['name'] = 'PG'
    info['author'] = 'Xinze-Zheng'
    info['secret'] = '1234569'
    response = requests.put(
        url='http://127.0.0.1:5000/register-pg', json=info)
    print(dict(response.json()))
    data = response.json()
    tmp = dict()
    tmp['id'] = data['id']
    tmp['row'] = 99
    tmp['col'] = 99
    tmp['color'] = random.randint(1, 10)
    response = requests.put(
        url='http://127.0.0.1:5000/update-pixel', json=tmp)
    return 'sent', 200
