# For this code, take a look at /face_recognition_server/server.py
# and adapt the code within that folder so that your poll.py process
# runs parallel to that code, and updates the encoding whenever necessary

# (You'll have to change it from two arrays to a dictionary, would make
# your life a lot easier) But what you need it to do is basically compare
# the existing dictionary in memory as to whether or not a particular encoding
# you grabbed from memory exists in the dictionary. If not, add it.
# Since studentIDs are unique, you can use that as the key pretty reliably.


# In addition to that, you'll have to adapt the code in 
# /face_recognition_server/server.py to update the database whenever a
# face is detected. We should decide if we want to store date/time or just a 
# boolean.


# The last thing we need to do is set up a forwarding server for the Pi 
# to the teacher front-end. This part shouldn't be too difficult, though
# we may have to get a little crafty with the way we handle the websocket
# since we don't have enough ports open to us.
#
# | RASPBERRY PI | <-----------> | VM | <-----------> | CLIENT(S) |
#
# From above, the VM should just listen on a particular port (443 in our
# case), and wait for a special packet to determine what to do.
#
# Examples
# Pi (I am pi) --> VM ==> forward camera stream to another socket
# Client (I am client) --> VM ==> VM sends camera stream to the socket

import http.server as http
import sys
import socketserver
import face_recognition
import asyncio
import websockets
import numpy as np
import pickle
import multiprocessing
import threading
import cv2
import poll
from time import perf_counter as now
import mysql.connector
import os

PROCESSES = []
THREADS = []
faceDict = {}
frame = None

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    database = "students"
)

def faceRec(signal):
    global frame
    global faceDict
    if not frame == None:
        while signal.is_set():
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            idList = []
            encodingList = []
            idDetected = None

            for key, value in faceDict.items():
                idList.append(key)
                encodingList.append(value)
                            
            for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(encodingList, face_encoding)

                    if True in matches:
                        first_match_index  = matches.index(True)
                        idDetected = idList[first_match_index]
                        #update database as present if not present


            for (top, right, bottom, left) in face_locations:
                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                #cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)


def socket(signal):
    async def handler(websocket, path):
        global frame
        print("Websocket opened")
        try:
            while signal.is_set():
                #receive frame
                frame = np.frombuffer(await websocket.recv(), dtype=np.uint8).reshape((480, 640, 3))
                
                #send frame to webpage if there is a request from client
                #await websocket.send(frame.tobytes())

        except websockets.exceptions.ConnectionClosed:
            print("Websocket closed")

    # Set up the listener
    print("Setting up socket")
    start_server = websockets.serve(ws_handler=handler, host='0.0.0.0', port=443)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def polling(man):
    global faceDict
    global mydb
    currentTime = now()

    print("entering the loop")
    while now() - currentTime < 1:
        pass
        
    print("exiting the loop")

    newFaces = {}
    mycursor = mydb.cursor()

    print("fetching from db")
    mycursor.execute("SELECT * FROM student_info WHERE ISNULL(Encoding) AND NOT ISNULL(Photo)")
    results = mycursor.fetchall()

    for x in results:
        print(x)

    # We're going to change the directory here
    try:
        # This is deterministic so we can hardcode the directory
        os.chdir("/opt/lampp/htdocs/photos")
        # But we may change it in the future, who knows
    except FileNotFoundError:
        # Good idea to catch any errors for error-prone ops
        pass

    for row in results:
        studentID = row[0]
        Photo = row[3]
        print("Student ID = ", studentID, " image name = ", Photo)
        try:
            newFaces[studentID] = face_recognition.load_image_file(Photo)
        except:
            print("Some error occured for follwing file: ", Photo)
            return

    for key, value in newFaces.items():
        # Use queues to send info to other process
        try:
            encodingToStore = face_recognition.face_encodings(value)[0].tobytes()
            faceDict[key] = encodingToStore
            print("successfully encoded")
            mycursor.execute("UPDATE student_info SET Encoding = %s WHERE studentID = %s", (encodingToStore, key))
            print("committing")
            mydb.commit()
        # We should only catch the index error, anything else we need to pay 
        # attention to while we're testing
        except IndexError:
            print("No face detected, or check for some other error")
            print("Setting Photo to NULL, and Needs_update to 1")
            mycursor.execute("UPDATE student_info SET Photo=%s, Needs_Update=%s WHERE studentID = %s", (None, "1", key))
            print("commiting set to null")
            mydb.commit()
    

def main(signal):
    #threads
    webs = threading.Thread(target=socket)
    frec = threading.Thread(target=faceRec)

    #processes stuff
    manager = multiprocessing.Manager()
    d = manager.dict()
    poll_handler = multiprocessing.Process(target=polling)

    THREADS.append(webs)
    THREADS.append(frec)

    PROCESSES.append(poll_handler)

    for t in THREADS:
        t.start()
    
    for p in PROCESSES:
        p.start()

    while True:
        pass
    

if __name__ == "__main__":
    try:
        signal = threading.Event()
        signal.set()
        main(signal)
    except KeyboardInterrupt:
        signal.clear()
        for t in THREADS:
            t.join()
        for p in PROCESSES:
            p.terminate()

