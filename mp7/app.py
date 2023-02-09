from calendar import weekday
from curses.ascii import isalpha
from email.policy import default
from tracemalloc import start
import zoneinfo
from flask import Flask, render_template, request, jsonify
import os
import requests
from datetime import *

app = Flask(__name__)

# Route for "/" (frontend):
@app.route('/')
def index():
  return render_template("index.html")


# Route for "/weather" (middleware):
@app.route('/weather', methods=["POST"])
def POST_weather():
  course = request.form["course"]
  course_code = ''
  course_num = ''
  for c in course:
    if str.isalpha(c):
      if c != ' ':
        course_code += c
    else :
      if c != ' ':
        course_num += c
  course_api_response = requests.get(f'http://127.0.0.1:34000/{str(course_code).upper()}/{course_num}')
  if course_api_response.status_code != 200:
    return "Course not found", 400
  print(course_api_response.json())
  print(course_api_response.json()['Days of Week'])
  weather_api_response = requests.get(f'https://api.weather.gov/gridpoints/ILX/{95},{71}/forecast/hourly')
  start_time = course_api_response.json()["Start Time"]
  start_time_min = int(start_time.split(' ')[0][-2:])
  start_time_hour = int(start_time.split(' ')[0][:2])
  if start_time.split(' ')[1] == 'PM' and start_time_hour != 12:
    start_time_hour += 12
  time = datetime.now(zoneinfo("America/Chicago")).replace(hour=start_time_hour, minute=start_time_min, second=0, microsecond=0)
  flag = True
  while flag:
    if time.timestamp() >= datetime.now().timestamp():
      for c in str(course_api_response.json()['Days of Week']):
        print(c + str(map_letter_weekday_to_number(c)) + str(time.weekday()))
        if int(map_letter_weekday_to_number(c)) == int(time.weekday()):
          flag = False
    if flag:
      time = time + timedelta(days = 1)
  print(time)
  
  result = 0
  for item in weather_api_response.json()['properties']['periods']:
    end_time = str(item['endTime'])
    end_date_time = datetime(int(end_time.split('-')[0]), int(end_time.split('-')[1]), int(end_time.split('-')[2][0:2]), int(end_time.split('T')[1].split(':')[0]))
    if end_date_time.timestamp() > time.timestamp():
      result = item
      break
  
  response = dict()
  response["course"] = course_api_response.json()["course"]
  response["nextCourseMeeting"] = str(time)
  start_time = str(item['startTime'])
  response["forecastTime"] = str(datetime(int(start_time.split('-')[0]), int(start_time.split('-')[1]), int(start_time.split('-')[2][0:2]), int(start_time.split('T')[1].split(':')[0])))
  
  if(datetime.now() + timedelta(days=6)).timestamp() < time.timestamp():
    response["temperature"] = "forecast unavailable"
    response["shortForecast"] = "forecast unavailable"
  else:
    response["temperature"] = result["temperature"]
    response["shortForecast"] = result["shortForecast"]

  return jsonify(response), 200


def map_letter_weekday_to_number(letter):
  
  if letter == 'M':
      return 0
  if letter ==  'T':
      return 1
  if letter == 'W':
      return 2
  if letter == 'R':
      return 3
  if letter == 'F':
      return 4
  if letter == _:
      return -1

