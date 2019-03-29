# Our server implementation basically has two things: a polling function
# that updates the database with face encodings whenever there are new entries,
# and a socket handler that will handle all the communication between a client
# and the Pi
#
# There are two processes: the main process and the poll process:
#     - The poll process will synchronize the shared memory dictionary of 
#         student IDs aand encodings, and also update the SQL database with 
#         the encodings whenever necessary
#     - The main process will run two threads: face recognition and the socket 
#         interface; the face recognition thread will process the frame every
#         second, and the socket interface will maintain the event loop to handle
#         incoming socket connections (two from the Pi for camera and parameters, 
#         and two from a client for the camera and parameters). The flow of data
#         from elements are as:
#
#         |------------|<-- params --|----------|<-- params --|------------|
#         |     Pi     |             |    VM    |             |   Client   |
#         |------------|-- frames -->|----------|-- frames -->|------------|

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

# Our global variables
PROCESSES = []
THREADS = []
RAW_FRAME = None
# Parameter format
PARAMS = {"angle": 2, "move": 1.5, "max": 120, "min": 60, "updated": False}

# This function runs in a thread concurrent to the main websocket handler 
# to do face recognition. It can take up to 3 seconds for this to run, so it's
# on another thread
def face_recognition_thread(dictionary, signal):
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
            # Update the table
            cursor = mydb.cursor()
            args = (stuID,)
            # Mark recognized faces as present
            cursor.execute("UPDATE student_info SET Present='1' WHERE studentID = %s", args)
            mydb.commit()
            # Update the dictionary by mutating it
            temp = dictionary[stuID]
            dictionary.pop(stuID)
            temp['seen'] = 1
            dictionary[stuID] = temp

    # Global frame object, this probably isn't necessary since we're not writing to it
    global RAW_FRAME
    # Set our current time so we use a non-blocking model to delay
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
                # print("Found face")
                unmatched_faces = [(a, b['encoding']) for a, b in dictionary.items() if b['seen'] != 1]
                known_encodings = [f[1] for f in unmatched_faces]
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                    # We found a match
                    if True in matches:
                        first_idx = matches.index(True)
                        name = unmatched_faces[first_idx][0]
                        # Call our update function since we've found a match
                        updatePresent(name)
        # Mark the end of the function
        curr_time = now()

# This process handles all the update and encoding functionality of the database,
# all wrapped up in a process to make it easier for us
def polling_process(dictionary):
    # This internal function synchronizes our encodings
    def syncEncoding():
        # Start a new DB connection
        mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            database = "students",
            use_pure = True # This is necessary to avoid encoding errors
        )
        # Grab the student ID and encodings that exist in the table
        cursor = mydb.cursor()
        cursor.execute("SELECT studentID, Encoding, Present FROM student_info WHERE NOT ISNULL(Encoding)")
        # Fetch the result
        results = cursor.fetchall()
        for row in results:
            # If the key isn't in the dictionary, add it
            if row[0] not in dictionary:
                # Reshape as the original numpy array
                dictionary[row[0]] = {"encoding": np.frombuffer(row[1], dtype=np.float64).reshape((128,)), \
                    "seen": row[2]}
            # Or if the present state does not match the seen state, update it
            elif row[2] != dictionary[row[0]]['seen']:
                dictionary.pop(row[0])
                dictionary[row[0]] = {"encoding": np.frombuffer(row[1], dtype=np.float64).reshape((128,)), \
                    "seen": row[2]}
    # This internal function updates the encodings in the table
    def updateEncodings():
        # Start a new DB connection
        mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            database = "students",
            use_pure = True # This is necessary to avoid encoding errors
        )
        # Grab the entries with photos but do not otherwise have an encoding
        cursor = mydb.cursor()
        cursor.execute("SELECT studentID, Photo FROM student_info WHERE ISNULL(Encoding) AND NOT ISNULL(Photo)")
        results = cursor.fetchall()
        # Change the working directory so we can grab the images
        try:
            os.chdir("/opt/lampp/htdocs/photos")
        except FileNotFoundError:
            return
        # Process the results
        for row in results:
            try:
                # Load image
                img = face_recognition.load_image_file(row[1])
                try:
                    enc = face_recognition.face_encodings(img)[0]
                    # Store the encoding (as bytes) into the database
                    cursor.execute("UPDATE student_info SET Encoding = %s \
                                WHERE studentID = %s", (enc.tobytes(), row[0]))
                    # Commit it
                    mydb.commit()
                except IndexError:
                    # If no face is found, the array call is out of bounds
                    # thus we need to need to update that db entry
                    cursor.execute("UPDATE student_info SET Photo=%s, \
                        Needs_Update=%s WHERE studentID = %s", (None, "1", row[0]))
                    mydb.commit()
            except FileNotFoundError:
                pass

    # Sync encodings at the start
    syncEncoding()
    # Mark the beginning
    curr_time = now()
    while True:
        # Poll every 2 seconds
        if now() - curr_time < 2:
            continue
        # Update encodings
        updateEncodings()
        # Synchronize the tables
        syncEncoding()
        # Mark the end
        curr_time = now()

# Receive images from the rpi camera and save that as the raw frame
async def rpi_handler(websocket, path):
    global RAW_FRAME
    try:
        # Keep the connection alive
        while True:
            val = None
            # Wait for the next frame, and set a timeout of 1 second
            try:
                val = await asyncio.wait_for(websocket.recv(), 2)
            except asyncio.TimeoutError:
                val = None
                return
            # If timed out, then we don't set the raw frame
            if val is not None:
                # Otherwise, decode from bytes into an image for interpretation
                RAW_FRAME = np.frombuffer(val, dtype=np.uint8).reshape((480, 640, 3))
    # We should only catch the connection being closed
    except websockets.exceptions.ConnectionClosed:
        pass

# Handle the client frame connection, forwards to client
async def client_handler(websocket, path):
    try:
        # Keep the connection alive
        while True:
            # Send frames at 0.15 second intervals to the client
            await asyncio.sleep(0.15)
            # Only send if the RAW_FRAME is not None
            if RAW_FRAME is not None:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50] # Encode at 50%
                f = cv2.imencode('.jpg', RAW_FRAME, encode_param)[1]
                # Wait a maximum of 1 second for this call
                try:
                    await asyncio.wait_for(websocket.send(f.tobytes()), 2)
                except asyncio.TimeoutError:
                    return
    except websockets.exceptions.ConnectionClosed:
        pass

# Handles the parameter connection, both for the rpi and client
# We used the same port for this because we figured we do not need
# as high of a throughput as the frame ports, thus we allow a wildcard
# endpoint at /ws/signal/* (as detailed in httpd-custom.conf)
async def param_handler(websocket, path):
    # We'll be writing the global PARAMS object, declare it
    global PARAMS
    try:
        # This is rpi connection, thus different logic
        if "rpi" in path:
            # Keep this connection open
            # Forward JSON package containing the parameter values for the robot to move
            # if the parameters have been updated
            while True:
                await asyncio.sleep(2)
                if PARAMS["updated"]:
                    await websocket.send(json.dumps(PARAMS))
                    PARAMS["updated"] = False
        # Client logic
        if "client" in path:
            # Recieve JSON packets from clients to forward to RPi
            while True:
                val = await websocket.recv()
                # Decode the payload
                PARAMS = json.loads(val)
    except websockets.exceptions.ConnectionClosed:
        pass

# Main function that is run on script execute
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
    rpi = websockets.serve(ws_handler=rpi_handler, host='0.0.0.0', port=3001)
    asyncio.get_event_loop().run_until_complete(rpi)
    cli = websockets.serve(ws_handler=client_handler, host='0.0.0.0', port=3002)
    asyncio.get_event_loop().run_until_complete(cli)
    param = websockets.serve(ws_handler = param_handler, host ='0.0.0.0',port=3003)
    asyncio.get_event_loop().run_until_complete(param)
    asyncio.get_event_loop().run_forever()
    

if __name__ == "__main__":
    try:
        # Need threading Event to join threads at termination
        signal = threading.Event()
        signal.set()
        main(signal)
    except KeyboardInterrupt:
        # Clean getaway
        signal.clear()
        for t in THREADS:
            t.join()
        for p in PROCESSES:
            p.terminate()
