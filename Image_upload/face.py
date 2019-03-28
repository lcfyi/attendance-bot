# For this code, take a look at /face_recognition_server/server.py
# and adapt the code within that folder so that your poll.py process
# runs parallel to that code, and updates the encoding whenever necessary

# (You'll have to change it from two arrays to a dictionary, would make
# your life a lot easier) But what you need it to do is basically compare
# the existing dictionary in memory as to whether or not a particular encoding
# you grabbed from memory exists in the dictionary. If not, add it.
# Since studentIDs are unique, you can use that as the key pretty reliably.


# In addition to that, you'll have to adapt the code in 
# /face_recognition_server/server.py to update the database whenever a
# face is detected. We should decide if we want to store date/time or just a 
# boolean.


# The last thing we need to do is set up a forwarding server for the Pi 
# to the teacher front-end. This part shouldn't be too difficult, though
# we may have to get a little crafty with the way we handle the websocket
# since we don't have enough ports open to us.
#
# | RASPBERRY PI | <-----------> | VM | <-----------> | CLIENT(S) |
#
# From above, the VM should just listen on a particular port (443 in our
# case), and wait for a special packet to determine what to do.
#
# Examples
# Pi (I am pi) --> VM ==> forward camera stream to another socket
# Client (I am client) --> VM ==> VM sends camera stream to the socket
