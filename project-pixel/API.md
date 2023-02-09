# Pixel API

### Introduction

- This middleware utilizes threads to control the traffic.
- The backend PGs are required to register in the middleware, and the middleware will fetch the pixels the backend wants to change with a particular time gap.
- MongoDB is used as database for backend servers information and recording the history of board.
- The frontend-changing pixel feature is implemented with traffic control method of using Netid verification.

## 0.Dependencies

- MongoDB server, default on port 27017

To run the middleware use:`flask run` or `python3 -m flask run`.

To use docker to build a mongoDB run: `docker run --name mongodb -d -p 27017:27017 mongo`

## 1.PG communication APIs

`PUT '/addPG'`: Every backend server is required to make put requst to this url to register. The middleware will check if there exists a PG with identical author and name in the DB, if it exists the data about that PG will be updated and otherwised recorded as new PG. After updating the PG, if PG's connection status is not 200, the thread will be restart to attempt to connect to PG again. If and only if a new PG is added, the middleware will send a unique id to the backend which is expected to be stored. The id serves as a security check to avoid PG being deleted/pause by people other than owner. TODO: Put restriction on the number of PGs every author can have.

`GET '/pauseServer/<id>/'`: Pause the corresponding communication thread for a backend server with <id>.

`GET '/resumeServer/<id>/'`: Resume the corresponding communication thread for a backend server with <id> from pause. Note if there exists connection issue with the backend server the thread is still blocked and should be reactivated via `'/restartServer/<id>/'`.

`GET '/restartServer/<id>/'`: Restart the corresponding communication thread fro a backend server with <id>. Will try to reconnect and resume the server.

`GET '/removeServer/<id>/'`: Kill the corresponding thread and remove the server info from cache and DB.

`GET '/pauseAll'`: Pause all servers.

`GET '/resumeAll'`: Resume all servers.

`GET '/restartAll'`: Restart all servers.

`GET '/clearDB'`: Remove all DB information about server, clear the caches and kill all threads.

## 2.Backend API requirement

`GET '/getChange'`: The middleware will make GET request to this url once server is registerd. The api must return a json file `{'changes': l}` where the `l` is a list of changes, each change in the list consists of 3 entries `[x, y, color]` which indicates the coordinates of the pixels want to be changed and the goal color.

For instance if a server changes to change pixels at (1, 2) and (200, 200) to first color in palette, json file should look like `{'changes': [[1,2,0], [200,200,0]]}`.

## 3.Frontend API

`GET '/changeByClick/<x>/<y>/<color>/<id>/'`: This api will receive request from the front-end, if the netid<id> if a valid netid and if time difference between the previous request made by this id and now exceeds the `secondInterval` in `FrontendManger`. The pixel at (x,y) will be updated to color. The default time gap requirement is 3s.

`GET '/servers'`: Render a html page of available servers and their status.

## 4.Frontend Modification

`index.html`: Adding netid textfield and color selections to enable the frontend pixel changes. The netid must be valid inorder to interact with the middleware. By click on the pixel board, user is able to update the gloabl board every 3 seconds. Currently the netid verification is not implememnted, so any non-empty netid will be able to update the board. TODO: Styling.

`server.html`: Render list of available servers, displaying connection status. TODO: Display more properties.
<img width="886" alt="image" src="https://user-images.githubusercontent.com/112009367/202830648-6dcbae77-4764-4c57-88e0-4bfc212f7f1f.png">
<img width="1339" alt="image" src="https://user-images.githubusercontent.com/112009367/202830671-a1cd443d-a60a-40a0-beef-f9f7bf4f801f.png">

## 5.Historical state recording API

`GET '/startRecording'`: Start recording the state of the view via threads, default is record every 10 seconds.

`GET '/pauseRecording'`: Pause recording by blocking the thread.

`GET '/resumeRecording'`: Resume recording from pause.

`GET '/getHistories'`: Return a json of the historical states of board in order. Return file can be very large without compression.

`GET '/deleteHistories'`: Delete the recording of board histories from DB.

## 6.Week2 Challenge evaluation

`How do we limit how often a PG can update the pixel board?`
  
Use threads to allow independent commnication between midlleware and backends.
Every thread will try to communicate with backend based on a given time interval
defined by the variable in the `ServerThread` class.

Robustness: When a request to backend has status code other than 200, the thread is blocked by `wait()` and can be only restarted by `GET '/restartAll'`. It is possible that when the traffic load is high, the time interval between communication might not be accurate as defined but the error in time should be acceptable.

Scalablity: Theoritically, middleware can lauch as many thread as it could. Additional features can be implemented in `ServerThread` and `ServerManager`class which is used by `app.py`.

`How do we allow a human-user to update the pixel board via the frontend, simultaneously with the PGs? How do we limit how often human-users can update the pixel board?`
  
The middleware exposed an API to allow frontend to change the state of board. The netid verification(requiring netid information of the class) and timestamp of request is used to restrict the rate every frontend user can update the board. The frontend also allow color selection.

Scalability: The middleware currently manages both verifying netid and timestamp, it is possible to let frontend to deal with timestamp verification to reduce the computing of the middleware.

Robustness: As long as the netid information of the class is provided, the middleware can reliably restrict the rate of access.

`How do we store/show the history of the pixel board? Can we “replay” the pixel board?`
  
The mongoDB is used to store the history of the board. An instance `HistoryThread` is lauched to record the history and has functionality of pause, resume, deletion.

Scalability: Currently the implementation store the entire board to DB, which takes a very large space. It is possible to only record the difference in state everytime to save space.

`How do PGs know the state of the pixel board? In future PGs, you may need to “defend” your part of the board from others overwriting it and must know if a PG need to change a pixel they’ve previously set.`

Currently, backends are expected to use `GET '/pixels/` to get the state of the board.

Scalability: The implementation can expose more API that allows backend to get the state of a particular area rather than the whole board to save bandwidth.

Robustness: Backends have to make the legal request.

`How do we ensure the image persists across restarts of the app?`
  
MongoDB is used to store the state of the board. Currently the app only load the information about registered PGs to the caches. TODO: Add method in `ServerDB` to allow getting the latest saved board history.
