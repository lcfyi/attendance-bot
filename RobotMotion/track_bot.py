import robot_control
import optical_sensor
import time
from servo_control import Servo_Control as sc

class TrackRobot(robot_control.Robot_Control):

    def __init__(self):
        self.leftSensor = optical_sensor.Optical_Sensor(6)
        self.rightSensor = optical_sensor.Optical_Sensor(13)
        self.status = "stopped"
        self.direction = 1

        self.x_pan = sc(26)
        self.y_pan = sc(19)
        self.x_pan.reset()
        self.y_pan.reset()

        self.x = [120, 150, 120, 90, 50, 30, 50, 90]
        self.y = [90, 110, 130]
        time.sleep(1)




    def checkTrack(self):
            current = time.perf_counter()
            while True:
                if (time.perf_counter() - current) >= 2 :
                    break
                # true when we detect white
                rightVal = self.leftSensor.read_sensor()
                leftVal = self.rightSensor.read_sensor()
                goStraight = rightVal and leftVal

                if goStraight:
                    if self.direction == 1:
                        self.goStraight()
                    else:
                        self.goBack()
                    if not self.status == "moving":
                        print("switch")
                        self.status = "moving"

                elif rightVal:
                    self.turnLeftImm()
                    if not self.status == "moving":
                        self.status = "moving"

                elif leftVal:
                    self.turnRightImm()
                    if not self.status == "moving":
                        self.status = "moving"

                else:
                    self.stop()
                    if not self.status == "stopped":
                        self.status = "stopped"

    def scan(self):
        for y in self.y:
            self.y_pan.change_angle(y)
            for x in self.x:
                self.x_pan.change_angle(x)
                currenttime = time.perf_counter()
                while time.perf_counter() - currenttime < 0.5:
                    pass
    def loop(self):
        try: 
            while True:
                self.checkTrack()
                if self.status == "stopped":
                    current = time.perf_counter()
                    while time.perf_counter() - current < 2:
                        pass
                    
                    self.direction *= -1
                    self.goStraight()
                    time.sleep(1)
                self.stop()
                self.scan()
                self.x_pan.reset()
                self.y_pan.reset()

        except KeyboardInterrupt:
            GPIO.cleanup() 
            pass


if __name__ == "__main__":
    import RPi.GPIO as GPIO 
    Robot = TrackRobot()
    try: 
        while True:
            Robot.checkTrack()
            if Robot.status == "stopped":
                current = time.perf_counter()
                while time.perf_counter() - current < 2:
                    pass
                
                Robot.direction *= -1
                Robot.goStraight()
                time.sleep(1)
            Robot.stop()
            Robot.scan()
            Robot.x_pan.reset()
            Robot.y_pan.reset()

    except KeyboardInterrupt:
        GPIO.cleanup() 
        pass
