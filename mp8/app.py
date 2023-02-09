from crypt import methods
from email.mime import image
import json
import logging
from unittest import skip
from flask import Flask, jsonify, send_file, render_template, request
import requests
import os
import io
import boto3
import base64
from botocore.exceptions import ClientError
from flask import Response
app = Flask(__name__)
colormap = 'twilight_shifted'
real = float(0.36)
imag = float(-0.09)
height = float(0.0024)
dim = int(512)
iter = int(128)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/all')
def all():
    return render_template('all.html')


@app.route('/moveUp', methods=['POST'])
def moveUp():
    global imag
    global height
    imag += float(0.25 * float(height))
    return 'Success', 200


@app.route('/moveDown', methods=['POST'])
def moveDown():
    global imag
    global height
    imag -= float(0.25 * float(height))
    return 'Success', 200


@app.route('/moveLeft', methods=['POST'])
def moveLeft():
    global real
    global height
    real -= 0.25 * height
    return 'Success', 200


@app.route('/moveRight', methods=['POST'])
def moveRight():
    global real
    global height
    real += 0.25 * height
    return 'Success', 200


@app.route('/zoomIn', methods=['POST'])
def zoomIn():
    global height
    height = height / 1.4
    return 'Success', 200


@app.route('/zoomOut', methods=['POST'])
def zoomOut():
    global height
    height = height * 1.4
    return 'Success', 200


@app.route('/smallerImage', methods=['POST'])
def smallerImage():
    global dim
    dim = round(int(dim) * (1 / 1.25))
    return 'Success', 200


@app.route('/largerImage', methods=['POST'])
def largerImage():
    global dim
    dim = int(dim * 1.25)
    return 'Success', 200


@app.route('/moreIterations', methods=['POST'])
def moreIteration():
    global iter
    iter = int(iter * 2)
    return 'Success', 200


@app.route('/lessIterations', methods=['POST'])
def lessIteration():
    global iter
    iter = int(iter / 2)
    return 'Success', 200


@app.route('/changeColorMap', methods=['POST'])
def changeColorMap():
    global colormap
    print(request.get_json())
    colormap = request.get_json()['colormap']
    return 'Success', 200


@app.route('/resetTo', methods=['POST'])
def resetTo():
    global colormap
    global height
    global real
    global imag
    global dim, iter
    jsonFile = request.get_json()
    colormap = jsonFile['colormap']
    height = float(jsonFile['height'])
    real = float(jsonFile['real'])
    imag = float(jsonFile['imag'])
    dim = int(jsonFile['dim'])
    iter = int(jsonFile['iter'])
    return "Success", 200


@app.route('/mandelbrot', methods=['GET'])
def mandelbrot():
    urlHeader = 'http://127.0.0.1:34000/mandelbrot/'
    urlTail = f'{colormap}/{real:f}:{imag:f}:{height:f}:{int(dim)}:{int(iter)}'
    print("url: " + urlHeader + urlTail)
    s3_client = boto3.client('s3', endpoint_url="http://127.0.0.1:9000",
                             aws_access_key_id='ROOTNAME', aws_secret_access_key='CHANGEME123')
    try:
        s3_client.head_object(Bucket='bucket', Key=urlTail)
    except ClientError as e:
        response = requests.get(urlHeader + urlTail)

        if response.status_code != 200:
            return "Error", 404

        fp = open('1.png', "wb")
        fp.write(response.content)
        fp.close()
        if upload_file('1.png', 'bucket', urlTail):
            print('Upload: ' + urlTail)
        return send_file("1.png", mimetype='image/gif'), 200
    else:
        s3_client.download_file('bucket', urlTail, '2.png')
        return send_file("2.png", mimetype='image/gif'), 200


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3', endpoint_url="http://127.0.0.1:9000",
                             aws_access_key_id='ROOTNAME', aws_secret_access_key='CHANGEME123')
    # try:
    #     s3_client.create_bucket(Bucket='b')
    # except ClientError as e:
    #     skip
    try:
        bucket = s3_client.create_bucket(Bucket='bucket')
    except ClientError as e:
        skip

    try:
        # response = s3_client.upload_file(file_name, bucket, object_name)
        s3_client.upload_file(file_name, 'bucket', object_name)
    except ClientError as e:
        return False
    return True


@app.route('/getState', methods=['GET'])
def getState():
    response = dict()
    response['colormap'] = colormap
    response['dim'] = dim
    response['height'] = height
    response['imag'] = imag
    response['iter'] = iter
    response["real"] = real
    return jsonify(response), 200


@app.route('/storage', methods=['GET'])
def getStore():
    s3 = boto3.resource('s3', endpoint_url="http://127.0.0.1:9000",
                        aws_access_key_id='ROOTNAME', aws_secret_access_key='CHANGEME123')
    bucket = s3.Bucket('bucket')
    response = list()
    for b in bucket.objects.all():
        bucket.download_file(b.key, '3.png')
        buffer = 'data:image/png;base64,'
        data = base64.b64encode(open("3.png", "rb").read())
        buffer += str(data)[2:]
        response.append({'key': b.key, 'image': buffer})
    jsonstr = json.dumps(response)
    print(jsonstr)
    return Response(json.dumps(response),  mimetype='application/json'), 200
