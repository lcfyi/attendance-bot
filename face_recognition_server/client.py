import cv2
import websockets
import asyncio
import multiprocessing
import threading
import numpy as np
import pickle 

THREADS = []

image = None
coords = None

def camera(signal):
    global image
    vc = cv2.VideoCapture(0)

    while signal.is_set():
        frame = vc.read()[1]
        # Convert the frame from BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # ret_frame = copy.deepcopy(manager[1])
        if coords is not None:
            # print("data")
            # print(ret_frame)
            iter_var = pickle.loads(coords)
            # for (top, right, bottom, left), name in zip(iter_var[0].tolist(), iter_var[1].tolist()):
            for (top, right, bottom, left), name in iter_var:
                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the image
        cv2.imshow('Video', frame)
        cv2.waitKey(20)

def websocket(signal):
    async def oof():
        global coords
        async with websockets.connect("ws://cpen291-16.ece.ubc.ca:443") as websocket:
            while signal.is_set():
                # await asyncio.sleep(0.033) # 30 fps
                # Send the frame
                if image is not None:
                    # print("Sending frame")
                    await websocket.send(image.tobytes())
                    # Receive the processed coordinates
                    coords = await websocket.recv()

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
