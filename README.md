# Watch (me nae-nae) bot

## Backend
Our server implementation basically has two things: a polling function that updates the database with face encodings whenever there are new entries, and a socket handler that will handle all the communication between a client and the Pi.

There are two processes: the main process and the poll process:
- The poll process will synchronize the shared memory dictionary of student IDs aand encodings, and also update the SQL database with the encodings whenever necessary
- The main process will run two threads: face recognition and the socket interface; the face recognition thread will process the frame every second, and the socket interface will maintain the event loop to handle incoming socket connections (two from the Pi for camera and parameters, and two from a client for the camera and parameters). The flow of data from elements are as:
```
        |------------|<-- params --|----------|<-- params --|------------|
        |     Pi     |             |    VM    |             |   Client   |
        |------------|-- frames -->|----------|-- frames -->|------------|
```

## Website
Our website has a homepage (of a random design), and a student and teacher area.

### Student
The student area will allow students to put in their student ID, name, photo, and a secret (provided by the teacher) to register their face into the database.

### Teacher
The teacher area will allow the teacher to:
- See the present members
- Set the parameters (speed of sweep and distance on track)
- Clear the attendance
- Generate new secrets (for student registration)
- Request that a student update their entry
- Display the camera feed
- View unclaimed secrets
- View currently registered students

It is password protected.
