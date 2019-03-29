import cv2
import websockets
import asyncio
import multiprocessing
import threading
import numpy as np
import pickle 
import RobotMotion.track_bot as bot
import json

THREADS = []

image = None
dick = {"angle":2, "move":1.5, "max":120, "min":60}

def camera(signal):
    global image
    vc = cv2.VideoCapture(0)
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    r = True
    while r and signal.is_set():
        r, img = vc.read()
        image = cv2.flip(img, -1)

def robot():
    rob = bot.TrackRobot()
    rob.servoTime(dick["angle"])
    rob.moveTime(dick["move"])
    rob.changeAngles(dick["max"], dick["min"])

async def paramAsy(signal):
    ws = await websockets.connect("/ws/signal/rpi")
    while signal.is_set():
        try:
            if not signal.is_set():
                return
            if not ws.open and signal.is_set():
                print("not open")
                ws = await websockets.connect("/ws/signal/rpi")
            try:
                while True:
                    dictionary = await websockets.recv()
                    val = json.loads(dictionary)
                    dick["angle"] = val["angle"]
                    dick["move"] = val["move"]
                    dick["max"] = val["max"]
                    dick["min"] = val["min"]
            except asyncio.TimeoutError:
                print("Timeout")
                ws.close()
        except websockets.exceptions.ConnectionClosed:
            print("Socket Closed")

async def camAsy(signal):
    ws = await websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/rpicam")
    while signal.is_set():
        try:
            if not signal.is_set():
                return
            if not ws.open and signal.is_set():
                print("Not open")
                ws = await websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/rpicam")
            if image is not None:
                try:
                    await asyncio.sleep(0.2)
                    img = image.tobytes()
                    await asyncio.wait_for(ws.send(img), 0.2)
                except asyncio.TimeoutError:
                    print("Timeout")
                    ws.close()
        except websockets.exceptions.ConnectionClosed:
            pass

def main(signal):
    manager = multiprocessing.Manager()
    dic = manager.dict()

    bot_process = multiprocessing.Process(target=robot, args=(dic,))

    PROCESSES.append(bot_process)
    cam = threading.Thread(target=camera, args=(signal,))

    THREADS.append(cam)
    for t in THREADS:
        t.start()
    for p in PROCESSES:
        p.start()

    await asyncio.gather(paramAsy(signal), camAsy(signal))

    while True:
        pass
asyncio.run(main(signal()))

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
