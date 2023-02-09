from flask import Flask, jsonify, render_template, request
import numpy as np
from ServerManager import ServerManager
from FrontendManager import FrontendManager
app = Flask(__name__)

# If set to True, DB will be loaded when app starts
# If set to Flase, DB will be cleared
LOAD_DB_WHEN_START = True

# Internal states
width = 400
height = 400
palette = ["#FFFFFF", "#C0C0C0", "#808080", "#000000",
           "#E95419", "#0024FF", "#A1DBE5", "#96AF50", "#FFFF00", "#F282D9", "#EEEEEE"]
board = np.zeros((width, height), np.unsignedinteger).tolist()
PGs = []
serverManager = ServerManager(board=board, loadDB=LOAD_DB_WHEN_START)
frontendManager = FrontendManager(board=board)
frontendNum = 0


@app.route('/', methods=["GET"])
def GET_index():
    '''Route for "/" (frontend)'''
    return render_template("index.html")


@app.route('/settings', methods=["GET"])
def GET_settings():
    result = {"width": width, "height": height, "palette": palette}
    return jsonify(result), 200


@app.route('/pixels', methods=["GET"])
def GET_pixels():
    result = {"pixels": board}
    return jsonify(result), 200


@app.route('/addPG', methods=["PUT"])
def addPG():
    data = request.json
    if not data:
        return 'Data is missing', 400
    # if 'name' not in data:
    #     return 'PG name is missing', 400

    # Validate packet:
    for requiredKey in ['name', 'url', 'author']:
        if requiredKey not in request.json.keys():
            return f'Key "{requiredKey}" missing', 400
    id = serverManager.addServer(data=data)
    if id != None:
        return jsonify({'id': str(id)}), 200
    else:
        return jsonify({'id': None}), 200


@app.route('/servers', methods=["GET"])
def getServers():
    serverList = serverManager.servers.values()
    serverList = sorted(serverList, key=lambda e: e.author)

    return render_template('server.html', data={"servers": serverList})


@app.route('/pauseServer/<id>/', methods=["GET"])
def pauseServerById(id):
    print(f'pause {id}')
    return serverManager.pauseServer(id)


@app.route('/restartServer/<id>/', methods=["GET"])
def restartServerById(id):
    return serverManager.restartServer(id=id)


@app.route('/resumeServer/<id>/', methods=["GET"])
def resumeServerById(id):
    return serverManager.resumeServer(id)


@app.route('/removeServer/<id>/', methods=["GET"])
def removeServerById(id):
    return serverManager.removeServer(id=id)


@app.route('/pauseAll', methods=["GET"])
def pauseAll():
    serverManager.pauseAll()
    return "All threads paused", 200


@app.route('/resumeAll', methods=["GET"])
def resumeAll():
    serverManager.resumeAll()
    return "All threads resumed", 200


@app.route('/restartAll', methods=['GET'])
def restartAll():
    serverManager.restartAll()
    return "All threads restarted", 200


@app.route('/clearDB', methods=['GET'])
def clearDB():
    serverManager.clearDB()
    return "Drop existing DB", 200


@app.route('/startRecording', methods=['GET'])
def startRecording():
    serverManager.StartRecordHistory()
    return "start", 200


@app.route('/pauseRecording', methods=['GET'])
def pauseRecording():
    return serverManager.pauseRecording()


@app.route('/resumeRecording', methods=['GET'])
def resumeRecording():
    return serverManager.resumeRecording()


@app.route('/getHistories', methods=['GET'])
def getHistories():
    l = list(serverManager.getHistory())
    if l:
        return jsonify({'histories': l}), 200
    return "No history", 400


@app.route('/deleteHistories', methods=['GET'])
def deleteHistories():
    return serverManager.deleteHistories()


@app.route('/changeByClick/<x>/<y>/<color>/<id>/')
def changeByClick(x, y, color, id):
    print(x, y, id, color)
    frontendManager.updateChange(id=id, x=x, y=y, color=color)
    return "Success", 200
