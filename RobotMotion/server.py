# demo time 
import http.server as http
import asyncio
import websockets
import socketserver
import multiprocessing
import cv2
import sys
from datetime import datetime as dt # For logging purposes
from servo_control import Servo_Control as sc
from track_bot import TrackRobot as TrackBot
import RPi.GPIO as GPIO
import os

# Keep track of our processes
PROCESSES = []

def log(message):
    print("[LOG] " + str(dt.now()) + " - " + message)

def camera(man):
    log("Starting camera")
    vc = cv2.VideoCapture(0)

    if vc.isOpened():
        r, f = vc.read()
    else:
        r = False

    while r:
        cv2.waitKey(20)
        r, f = vc.read()
        f = cv2.resize(f, (640, 480))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 25]
        man[0] = cv2.imencode('.jpg', f, encode_param)[1]

# HTTP server handler
def server():
    server_address = ('0.0.0.0', 8000)
    # Directory of the webpage
    web_dir = os.path.join(os.path.dirname(__file__), "webpage")
    # Change to the directory of the webpage
    os.chdir(web_dir)

    if sys.version_info[1] < 7:
        class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.HTTPServer):
            pass
        httpd = ThreadingHTTPServer(server_address, http.SimpleHTTPRequestHandler)
    else:
        httpd = http.ThreadingHTTPServer(server_address, http.SimpleHTTPRequestHandler)
    log("Server started")
    httpd.serve_forever()

def socket(man, qx, qy, qmov):
    # Will handle our websocket connection for frames
    async def handlerFrames(websocket, path):
        log("Frame socket opened")
        try:
            while True:
                await asyncio.sleep(0.033) # 30 fps
                await websocket.send(man[0].tobytes())
        except websockets.exceptions.ConnectionClosed:
            log("Frame socket closed")

    # Handles our websocket connection for our pan angles
    async def handlerX(websocket, path):
        log("X socket opened")
        try:
            while True:
                val = await websocket.recv()
                qx.put(val)
        except websockets.exceptions.ConnectionClosed:
            log("X socket closed")

    # Handles our websocket connection for our tilt angles
    async def handlerY(websocket, path):
        log("Y socket opened")
        try:
            while True:
                val = await websocket.recv()
                qy.put(val)
        except websockets.exceptions.ConnectionClosed:
            log("Y socket closed")

    # Handles our websocket connection for our movements
    async def handlerMovement(websocket, path):
        log("Movement socket opened")
        # Robot = ManualRobot.ManualRobot()
        try:
            man[1] = False
            while True:
                val = await websocket.recv()
                log(val)
                qmov.put(val)
        except websockets.exceptions.ConnectionClosed:
            man[1] = True
            log("Movement socket closed")

    log("Starting socket handler")
    # Create the awaitable object
    start_server = websockets.serve(ws_handler=handlerFrames, host='0.0.0.0', port=8585)
    # Start the server, add it to the event loop
    asyncio.get_event_loop().run_until_complete(start_server)
    # Create the awaitable object
    start_serverX = websockets.serve(ws_handler=handlerX, host='0.0.0.0', port=8586)
    # Start the server, add it to the event loop
    asyncio.get_event_loop().run_until_complete(start_serverX)
    # Create the awaitable object
    start_serverY = websockets.serve(ws_handler=handlerY, host='0.0.0.0', port=8587)
    # Start the server, add it to the event loop
    asyncio.get_event_loop().run_until_complete(start_serverY)
    # Create the awaitable object
    start_serverMove = websockets.serve(ws_handler=handlerMovement, host='0.0.0.0', port=8588)
    # Start the server, add it to the event loop
    asyncio.get_event_loop().run_until_complete(start_serverMove)
    # Registered our websocket connection handler, thus run event loop forever
    asyncio.get_event_loop().run_forever()

def robot(man):
    log("Robot started")
    robot = TrackBot()
    stopped = False
    while True:
        if man[1]:
            robot.loop()
            stopped = False
        elif not stopped:
            robot.stop()
            stopped = True

def main():
    queueX = multiprocessing.Queue()
    queueY = multiprocessing.Queue()
    queueMove = multiprocessing.Queue()
    manager = multiprocessing.Manager()
    lst = manager.list()
    # Frame control logic
    lst.append(None)
    # Autonomous control logic
    lst.append(True) # If true, robot is autonomous
    # Host the page, creating the server
    http_server = multiprocessing.Process(target=server)
    # Set up our websocket handler
    socket_handler = multiprocessing.Process(target=socket, args=(lst, queueX, queueY, queueMove,))
    # Set up our camera
    camera_handler = multiprocessing.Process(target=camera, args=(lst,))
    # Set up our robot
    robot_handler = multiprocessing.Process(target=robot, args=(lst,))
    # Add 'em to our list
    PROCESSES.append(camera_handler)
    PROCESSES.append(http_server)
    PROCESSES.append(socket_handler)
    PROCESSES.append(robot_handler)
    for p in PROCESSES:
        p.start()
    # Wait forever
    # setup servo classes here
    pan_servo = sc(12)
    tilt_servo = sc(13)
    # Set up manual robot here
    # manual_robot = ManualBot()
    while True:
        # call servo functions here
        if not queueX.empty():
            # here for x
            # log("X: " + str(queueX.get()))
            dlt = int(queueX.get()) / 2
            # log(str(dlt))
            pan_servo.change_angle_delta(dlt)
        if not queueY.empty():
            # here for y
            # log("Y: " + str(queueY.get()))
            dlt = int(queueY.get()) / 2
            # log(str(dlt))
            tilt_servo.change_angle_delta(dlt)
        if not lst[1]:
            if not queueMove.empty():
                manual_robot.move(queueMove.get())

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for p in PROCESSES:
            p.terminate()
        GPIO.cleanup()
