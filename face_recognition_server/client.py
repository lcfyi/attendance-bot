import cv2
import websockets
import asyncio
import multiprocessing
import threading
import numpy as np
import pickle 

THREADS = []

image = None

def camera(signal):
    global image
    vc = cv2.VideoCapture(0)
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    r = True
    while r and signal.is_set():
        r, img = vc.read()
        image = cv2.flip(img, -1)

def websocket(signal):
    async def oof():
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

    asyncio.new_event_loop().run_until_complete(oof())
    asyncio.get_event_loop().run_forever()

def main(signal):
    cam = threading.Thread(target=camera, args=(signal,))
    socks = threading.Thread(target=websocket, args=(signal,))

    THREADS.append(cam)
    THREADS.append(socks)
    for t in THREADS:
        t.start()
    
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
