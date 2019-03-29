import cv2
import websockets
import asyncio
import multiprocessing
import threading
import numpy as np
from time import perf_counter as now
from track_bot import TrackRobot as bot
import json
from time import sleep as nap

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
    # Pass it the shared memory parameter
    rob = bot(dictionary)
    while True:
        # Start the robot tasks
        rob.checkTrack()
        # Grab the status
        if rob.status == "stopped":
            # Scan
            rob.scan()
            # Reset the pan and tilt servos
            rob.x_pan.reset()
            rob.y_pan.reset()
            # Reverse the direction
            rob.direction *= -1
            # Set the direction
            if rob.direction < 0:
                rob.goBack()
            else:
                rob.goStraight()
            # Set a timeout when it gets to the end of the track
            curr_time = now()
            while now() - curr_time < 0.2:
                continue
        # Stop and do it all over again
        rob.stop()
        rob.scan()
        rob.x_pan.reset()
        rob.y_pan.reset()

# Parameter websocket, updates the dictionary
async def paramAsy(dictionary, signal):
    # While the thread should continue
    while signal.is_set():
        # Wrap everything in an unconditional try-catch to ensure
        # that the Pi never errors out while sending data, and that 
        # it will always try to restore the connection
        try:
            # Open the connection
            # print("Start the params socket")
            ws = await asyncio.wait_for(websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/signal/rpi"), 3)
            # Second while loop
            while signal.is_set():
                asyncio.sleep(0.15)
                # If the socket isn't open for some reason, open it again
                if not ws.open and signal.is_set():
                    ws = await asyncio.wait_for(websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/signal/rpi"), 3)
                # Grab the dictionary
                ret = await ws.recv()
                val = json.loads(ret)
                # Update our values with the values from the socket
                dictionary["angle"] = val["angle"]
                dictionary["move"] = val["move"]
                dictionary["max"] = val["max"]
                dictionary["min"] = val["min"]
        except:
            # print("Error on params socket")
            try:
                if ws.open:
                    ws.close()
            except AttributeError:
                # print("Attribute error")
                pass
            # Close the socket if it's still open, and keep going
            # pass
            # if ws.open:
            #     ws.close()

# Camera websocket, should start up if fails and run forever
async def camAsy(signal):
    # Same as above
    while signal.is_set():
        try:
            # Start the connection
            # print("Start the frame socket")
            ws = await asyncio.wait_for(websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/rpicam"), 3)
            while signal.is_set():
                asyncio.sleep(0.15)
                # If the socket isn't open, open it again
                if not ws.open and signal.is_set():
                    ws = await asyncio.wait_for(websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/rpicam"), 3)
                # If the image isn't none, send it
                if IMAGE is not None:
                    await asyncio.wait_for(ws.send(IMAGE.tobytes()), 0.5)
        except:
            # print("Error on frames socket")
            try:
                if ws.open:
                    ws.close()
            except AttributeError:
                # print("Attribute error")
                pass
            # if ws.open:
            #     ws.close()

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

    nap(5)
    # Add our tasks to the event loop and run them concurrerntly
    await asyncio.gather(paramAsy(dic, signal), camAsy(signal))

if __name__ == "__main__":
    try:
        signal = threading.Event()
        signal.set()
        asyncio.get_event_loop().run_until_complete(main(signal))
    except KeyboardInterrupt:
        # Clean up the setup
        signal.clear()
        for t in THREADS:
            t.join()
        for p in PROCESSES:
            p.terminate()
