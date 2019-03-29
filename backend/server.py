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

import sys
import face_recognition
import asyncio
import websockets
import numpy as np
import json
import multiprocessing
import threading
import copy
import cv2
from time import perf_counter as now
import mysql.connector
import os

PROCESSES = []
THREADS = []
RAW_FRAME = None
PARAMS = {"angle": 2, "move": 1.5, "max": 120, "min": 60, "updated": False}

# This function runs in a thread concurrent to the main websocket handler 
# to do face recognition. It can take its time
def face_recognition_thread(dictionary, signal):
    print("Face recognition thread started")
    # Connect to the database, since we'll need to update on face detection
    # Create a helper function to mark the student as present
    def updatePresent(stuID):
        if stuID != "Unknown":
            mydb = mysql.connector.connect(
                host = "localhost",
                user = "root",
                database = "students",
                use_pure = True # This is necessary to avoid encoding errors
            )
            print("Face recoginition DB connection successful")
            print("Updating entry for ", stuID)
            # Update the table
            cursor = mydb.cursor()
            args = (stuID,)
            #Mark recognized faces as present
            cursor.execute("UPDATE student_info SET Present='1' WHERE studentID = %s", args)
            mydb.commit()
            # Update the dictionary by mutating it
            temp = dictionary[stuID]
            dictionary.pop(stuID)
            temp['seen'] = 1
            dictionary[stuID] = temp

    # Global frame object
    global RAW_FRAME
    curr_time = now()
    while signal.is_set():
        if now() - curr_time < 1:
            continue
        if RAW_FRAME is not None:
            # Make a copy of the current frame to do stuff with
            curr_frame = copy.deepcopy(RAW_FRAME)
            # Create a dictionary for matches
            face_names = []
            face_locations = []
            rgb_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2RGB)
            # Do the encoding logic
            face_locations = face_recognition.face_locations(rgb_frame)
            # This encodes each face found with the above expression
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Get the unmatched faces
            if len(face_locations) != 0:
                print("Found face")
                unmatched_faces = [(a, b['encoding']) for a, b in dictionary.items() if b['seen'] != 1]
                known_encodings = [f[1] for f in unmatched_faces]
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                    # We found a match
                    if True in matches:
                        first_idx = matches.index(True)
                        name = unmatched_faces[first_idx][0]
                        updatePresent(name)
            print(now(), " end face")
        curr_time = now()

# This process handles all the update and encoding functionality of the database,
# all wrapped up in a process to make it easier for us
def polling_process(dictionary):
    print("Polling process started")
    def syncEncoding():
        # Start a new DB connection
        mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            database = "students",
            use_pure = True # This is necessary to avoid encoding errors
        )
        print("Synchronizing encodings")
        # Grab the student ID and encodings that exist in the table
        cursor = mydb.cursor()
        cursor.execute("SELECT studentID, Encoding, Present FROM student_info WHERE NOT ISNULL(Encoding)")
        # Fetch the result
        results = cursor.fetchall()
        for row in results:
            # If the key isn't in the dictionary, add it
            if row[0] not in dictionary:
                print("New results")
                print((row[0], row[2]))
                # Reshape as the original numpy array
                dictionary[row[0]] = {"encoding": np.frombuffer(row[1], dtype=np.float64).reshape((128,)) \
                    , "seen": row[2]}
            # Or if the present state does not match the seen state, update it
            elif row[2] != dictionary[row[0]]['seen']:
                print("Updated results")
                print((row[0], row[2]))
                dictionary.pop(row[0])
                dictionary[row[0]] = {"encoding": np.frombuffer(row[1], dtype=np.float64).reshape((128,)) \
                    , "seen": row[2]}
    
    def updateEncodings():
        # Start a new DB connection
        mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            database = "students",
            use_pure = True # This is necessary to avoid encoding errors
        )
        print("Updating encodings")
        # Grab the entries with photos but do not otherwise have an encoding
        cursor = mydb.cursor()
        cursor.execute("SELECT studentID, Photo FROM student_info WHERE ISNULL(Encoding) AND NOT ISNULL(Photo)")
        results = cursor.fetchall()
        # Change the working directory so we can grab the images
        try:
            os.chdir("/opt/lampp/htdocs/photos")
        except FileNotFoundError:
            print("FileNotFoundError")
            return
        # Process the results
        for row in results:
            print(row)
            try:
                #load image
                img = face_recognition.load_image_file(row[1])
                try:
                    enc = face_recognition.face_encodings(img)[0]
                    # Store the encoding (as bytes) into the database
                    cursor.execute("UPDATE student_info SET Encoding = %s \
                                WHERE studentID = %s", (enc.tobytes(), row[0]))
                    # Commit it
                    mydb.commit()
                except IndexError:
                    #if no face is found, the array call is out of bounds
                    #we need to need to update that db entry
                    print("No face found, photo needs update")
                    cursor.execute("UPDATE student_info SET Photo=%s, \
                        Needs_Update=%s WHERE studentID = %s", (None, "1", row[0]))
                    mydb.commit()
            except FileNotFoundError:
                print("File not found for ", row[1])
                pass

    syncEncoding()
    curr_time = now()
    while True:
        #poll every 2 seconds
        if now() - curr_time < 2:
            continue
            # If our rate limit has been exceeded, do stuff
        updateEncodings()
        syncEncoding()
        curr_time = now()

#receive images from the rpi camera and save that as the raw frame
async def rpi_handler(websocket, path):
    global RAW_FRAME
    print("RPi frame socket opened")
    try:
        #image consumer loop
        while True:
            val = None
            try:
                print("Receiving")
                val = await asyncio.wait_for(websocket.recv(), 1)
                # print("Received")
            except asyncio.TimeoutError:
                val = None
                print("RPi timeout")
            if val is not None:
                #decode from bytes into an image for interpretation
                RAW_FRAME = np.frombuffer(val, dtype=np.uint8).reshape((480, 640, 3))

    except websockets.exceptions.ConnectionClosed:
        print("RPi frame socket closed")

async def client_handler(websocket, path):
    print("Raw frame socket opened")
    try:
        #frame forwarding loop
        while True:
            #send frames at 0.15 second intervals to the client
            await asyncio.sleep(0.15)
            if RAW_FRAME is not None:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50] # Encode at 15%
                f = cv2.imencode('.jpg', RAW_FRAME, encode_param)[1]
                try:
                    print("Sending")
                    await asyncio.wait_for(websocket.send(f.tobytes()), 1)
                    # print("Sent")
                except asyncio.TimeoutError:
                    print("Raw timeout")
    except websockets.exceptions.ConnectionClosed:
        print("Raw frame socket closed")

async def param_handler(websocket, path):
    global PARAMS
    print("Param socket is opened")
    print(path)
    try:
        if "rpi" in path:
            print("RPi connection")
            # Keep this connection open
            # Forward JSON package containing the parameter values for the robot to move
            while True:
                await asyncio.sleep(2)
                if PARAMS["updated"]:
                    await websocket.send(json.dumps(PARAMS))
                    print("Sent value")
                    PARAMS["updated"] = False
        if "client" in path:
            print("Client connection")
            # Recieve JSON packets from clients to forward to RPi
            while True:
                val = await websocket.recv()
                print("Received value ", json.loads(val))
                PARAMS = json.loads(val)
    except websockets.exceptions.ConnectionClosed:
        print("Param socket closed")
    param_data = await websockets.recv()



def main(signal):
    # Process for our database update functionality
    manager = multiprocessing.Manager()
    dic = manager.dict()
    poll_handler = multiprocessing.Process(target=polling_process, args=(dic,))
    PROCESSES.append(poll_handler)

    # Our single thread, organized by the global array
    frt = threading.Thread(target=face_recognition_thread, args=(dic, signal))
    THREADS.append(frt)

    # Start our processes and threads
    for t in THREADS:
        t.start()
    for p in PROCESSES:
        p.start()

    # Set up the server that will handle all socket connections, will run
    # in the main process
    print("Setting up socket")
    rpi = websockets.serve(ws_handler=rpi_handler, host='0.0.0.0', port=3001)
    asyncio.get_event_loop().run_until_complete(rpi)
    cli = websockets.serve(ws_handler=client_handler, host='0.0.0.0', port=3002)
    asyncio.get_event_loop().run_until_complete(cli)
    param = websockets.serve(ws_handler = param_handler, host ='0.0.0.0',port=3003)
    asyncio.get_event_loop().run_until_complete(param)
    asyncio.get_event_loop().run_forever()
    

if __name__ == "__main__":
    try:
        #Need threading Event to join threads at termination
        signal = threading.Event()
        signal.set()
        main(signal)
    except KeyboardInterrupt:
        signal.clear()
        for t in THREADS:
            t.join()
        for p in PROCESSES:
            p.terminate()
