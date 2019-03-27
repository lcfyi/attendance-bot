import face_recognition
import numpy
from time import perf_counter as now
import mysql.connector
import base64


mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    database = "students"
)

currentTime = now()

print("entering the loop")
while now() - currentTime < 1:
    pass
    
print("exiting the loop")

newFaces = {}
mycursor = mydb.cursor()

print("fetching from db")
mycursor.execute("SELECT * FROM student_info WHERE ISNULL(Encoding) AND NOT ISNULL(Photo)")
results = mycursor.fetchall()

for x in results:
    print(x)

for row in results:
    studentID = row[0]
    Photo = row[3]
    print("Student ID = ", studentID, " image name = ", Photo)
    newFaces[studentID] = face_recognition.load_image_file(Photo)


for key, value in newFaces.items():
    #use queues to send info to other process
    encodingToStore = face_recognition.face_encodings(value)[0]
    print("successfully encoded")
    mycursor.execute("UPDATE student_info SET Encoding = %s WHERE studentID = %s", (encodingToStore.tobytes(), key))
    print("committing")
    mydb.commit()


