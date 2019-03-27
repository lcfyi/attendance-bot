import http.server as http
import sys
import socketserver
import face_recognition
import asyncio
import websockets
import numpy as np
import pickle

leslie_image = face_recognition.load_image_file("leslie.jpg")
leslie_encoding = face_recognition.face_encodings(leslie_image)[0]

known_face_encodings = [
    leslie_encoding
]
known_face_names = [
    "Leslie"
]

face_locations = []
face_encodings = []
face_names = []

def socket():
    async def handler(websocket, path):
        print("Websocket opened")
        try:
            while True:
                frame = np.frombuffer(await websocket.recv(), dtype=np.uint8).reshape((480, 640, 3))
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                face_names = []
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]

                    face_names.append(name)
                print(face_locations)
                # print(face_names)
                # print(np.array([face_locations, face_names]).tobytes())
                # print(np.array([face_locations, face_names]).shape)
                # print(np.array([face_locations, face_names]).dtype)
                # await websocket.send(np.array([face_locations, face_names]).tobytes())
                await websocket.send(pickle.dumps(zip(face_locations, face_names)))
                print(face_locations)

        except websockets.exceptions.ConnectionClosed:
            print("Websocket closed")

    # Set up the listener
    print("Setting up socket")
    start_server = websockets.serve(ws_handler=handler, host='0.0.0.0', port=443)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    socket()