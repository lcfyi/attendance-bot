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
        r, image = vc.read()
        # Convert the frame from BGR to RGB
        # image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # ret_frame = copy.deepcopy(manager[1])
        # if coords is not None:
            # print("data")
            # print(ret_frame)
            # iter_var = pickle.loads(coords)
            # # for (top, right, bottom, left), name in zip(iter_var[0].tolist(), iter_var[1].tolist()):
            # for (top, right, bottom, left), name in iter_var:
            #     # Draw a box around the face
            #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            #     # Draw a label with a name below the face
            #     cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            #     font = cv2.FONT_HERSHEY_DUPLEX
            #     cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the image
        cv2.imshow('Video', image)
        cv2.waitKey(20)

def websocket(signal):
    async def oof():
        ws = await websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/rpicam")
        while signal.is_set():
            # await asyncio.sleep(0.033) # 30 fps
            # Send the frame
            if not ws.open and signal.is_set():
                print("Not open")
                ws = await websockets.connect("ws://cpen291-16.ece.ubc.ca/ws/rpicam")
            if image is not None:
                # print("Sending frame")
                # img = image.tobytes()
                try:
                    await asyncio.sleep(0.033)
                    # print("Sending")
                    img = image.tobytes()
                    await asyncio.wait_for(ws.send(img), 2)
                    # print("Sent")
                except asyncio.TimeoutError:
                    pass
                # Receive the processed coordinates
    # async def connect():
    #     try:
    #         async with websockets.connect('ws://cpen291-16.ece.ubc.ca/signal/f') as ws:
    #             while True:
    #                 login_action = {"action": "login", "data": "cam"}
    #                 await websocket.send(json.dumps(login_action))
    #                 await asyncio.sleep(10)
    #     except:
    #         pass

    # cors = asyncio.wait([oof()])
    # asyncio.get_event_loop()
    asyncio.run(oof())

def main(signal):
    # Setup steps again
    # manager = multiprocessing.Manager()
    # lst = manager.list()
    # # First element is the frame
    # lst.append(None)
    # # Second element is the coordinates
    # lst.append(None)
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
