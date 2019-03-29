from robot_control import Robot_Control
from optical_sensor import Optical_Sensor
import time
from servo_control import Servo_Control as sc

class TrackRobot(Robot_Control):

    def __init__(self, dictionary):
        #Setup Sensors, parameters and servos
        self.leftSensor = Optical_Sensor(6)
        self.rightSensor = Optical_Sensor(13)
        self.status = "stopped"
        self.direction = 1
        self.params = dictionary
        self.x_pan = sc(26)
        self.y_pan = sc(19)
        self.x_pan.reset()
        self.y_pan.reset()

        # Predetermined angles at which the robot
        # waits to capture a frame
        self.x = [120, 100, 80, 60]
        self.y = [90, 110]

    def changeAngles(self, max, min):
        if max < 150 and min > 10:
            for i in range(0, 3):
                self.x[i] = (max - min)/3*i+min

    def servoTime(self, time):
        self.servo_time = time

    def moveTime(self, time):
        self.move_time = time

    def checkTrack(self):
            current = time.perf_counter()
            track = 0
            while True:
                if (time.perf_counter() - current) >= self.params["move"]:
                    break
                # true when we detect white
                rightVal = not self.leftSensor.read_sensor()
                leftVal = not self.rightSensor.read_sensor()

                goStraight = rightVal and leftVal

                if goStraight:
                    if self.direction == 1:
                        self.goStraight()
                    else:
                        self.goBack()
                    if not self.status == "moving":
                        #print("switch")
                        self.status = "moving"

                else:
                    if track >= 5:
                        self.stop()
                        if not self.status == "stopped":
                            self.status = "stopped"
                            break
                    track += 1

    def scan(self):
        #Do the set pan and tilt routine defined by instance arrays
        for y in self.y:
            self.y_pan.change_angle(y)
            for x in self.x:
                self.x_pan.change_angle(x)
                currenttime = time.perf_counter()
                while time.perf_counter() - currenttime < self.params["angle"]:
                    pass

    
if __name__ == "__main__":
    import RPi.GPIO as GPIO 
    Robot = TrackRobot()
    try: 
        while True:
            #check track color
            Robot.checkTrack()
            if Robot.status == "stopped":
                #reach end of track and perform scan
                Robot.scan()
                Robot.x_pan.reset()
                Robot.y_pan.reset()
                Robot.direction *= -1
                #print("going")
                if Robot.direction < 0:
                    Robot.goBack()
                else:
                    Robot.goStraight()
                time.sleep(1)
            #status is still "moving"
            #continue in the same direction after scanning
            Robot.stop()
            Robot.scan()
            Robot.x_pan.reset()
            Robot.y_pan.reset()

    except KeyboardInterrupt:
        GPIO.cleanup() 
        pass
