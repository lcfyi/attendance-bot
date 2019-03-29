import cv2
import websockets
import asyncio
import multiprocessing
import threading
import numpy as np
from time import perf_counter as now
from track_bot import TrackRobot as bot
import json

THREADS = []
PROCESSES = []

IMAGE = None

# Thread handler for our cmaera
def camera(signal):
    global IMAGE
    vc = cv2.VideoCapture(0)
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Set the entry variable to true
    r = True
    while r and signal.is_set():
        # Set r based on camera failures
        r, img = vc.read()
        # Flip the image
        IMAGE = cv2.flip(img, -1)

# Process for our robot
def robot(dictionary):
    rob = bot(dictionary)
    while True:
        rob.checkTrack()
        #print(Robot.status)
        if rob.status == "stopped":
            rob.scan()
            rob.x_pan.reset()
            rob.y_pan.reset()
            rob.direction *= -1
            # print("going")
            if rob.direction < 0:
                rob.goBack()
            else:
                rob.goStraight()
            curr_time = now()
            while now() - curr_time < 0.2:
                continue
        rob.stop()
        rob.scan()
        rob.x_pan.reset()
        rob.y_pan.reset()

# Parameter websocket, updates the dictionary
async def paramAsy(dictionary, signal):
    ws = await websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/signal/rpi")
    # print("Parameter socket opened")
    while signal.is_set():
        try:
            if not ws.open and signal.is_set():
                # print("not open")
                ws = await websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/signal/rpi")
            ret = await ws.recv()
            val = json.loads(ret)
            # print(val)
            dictionary["angle"] = val["angle"]
            dictionary["move"] = val["move"]
            dictionary["max"] = val["max"]
            dictionary["min"] = val["min"]
        except websockets.exceptions.ConnectionClosed:
            # print("Socket Closed")
            pass

# Camera websocket, should start up if fails and run forever
async def camAsy(signal):
    ws = await websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/rpicam")
    # print("Camera socket opened")
    while signal.is_set():
        try:
            if not ws.open:
                print("Not open")
                ws = await websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/rpicam")
            if IMAGE is not None:
                try:
                    await asyncio.sleep(0.15)
                    await asyncio.wait_for(ws.send(IMAGE.tobytes()), 0.5)
                except asyncio.TimeoutError:
                    # print("Timeout")
                    ws.close()
        except websockets.exceptions.ConnectionClosed:
            # Catch error, open again
            pass

async def main(signal):
    # Process setup
    manager = multiprocessing.Manager()
    dic = manager.dict()
    dic["angle"] = 2
    dic["move"] = 1.5
    dic["max"] = 120
    dic["min"] = 60
    dic["updated"] = True
    bot_process = multiprocessing.Process(target=robot, args=(dic,))
    PROCESSES.append(bot_process)

    # Thread setup
    cam = threading.Thread(target=camera, args=(signal,))
    THREADS.append(cam)
    
    # Start all processes and threads
    for t in THREADS:
        t.start()
    for p in PROCESSES:
        p.start()

    # Start all of them 
    await asyncio.gather(paramAsy(dic, signal), camAsy(signal))

if __name__ == "__main__":
    try:
        signal = threading.Event()
        signal.set()

        asyncio.get_event_loop().run_until_complete(main(signal))
    except KeyboardInterrupt:
        # print("Trying to stop")
        signal.clear()
        for t in THREADS:
            t.join()
        for p in PROCESSES:
            p.terminate()
