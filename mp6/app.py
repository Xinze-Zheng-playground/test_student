from genericpath import exists
from flask import Flask, render_template, send_file, request
import os

app = Flask(__name__)

# Route for "/" for a web-based interface to this micro-service:
@app.route('/')
def index():
  return render_template("index.html")

cnt = 0

# Extract a hidden "uiuc" GIF from a PNG image:
@app.route('/extract', methods=["POST"])
def extract_hidden_gif():
  # ...your code here...
  if not os.path.exists("temp"):
    os.mkdir("temp")
  os.system("make clean")
  os.system("make")
  global cnt
  if not os.path.exists("request"):
    os.mkdir("request")
  request.files['png'].save(f"request/{request.files['png'].filename}")
  cond = os.system(f"./png-extractGIF sample/{request.files['png'].filename} temp/{cnt}.gif")

  
  if cond == 0:
    request.files['png'].save(f"temp/{cnt}.png")
    temp = cnt
    cnt += 1
    return send_file(f"temp/{temp}.gif", mimetype='image/gif'), 200
  return "File does not contain a hidden gif", 500
# Get the nth saved "uiuc" GIF:
@app.route('/extract/<int:image_num>', methods=['GET'])
def extract_image(image_num):
  # ...your code here...
  if exists(f"temp/{image_num}.gif"):
    return send_file(f"temp/{image_num}.gif", mimetype='image/gif'), 200
  return "Does not exist such file", 500
