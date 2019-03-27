import robot_control
import optical_sensor
import time
from servo_control import Servo_Control as sc

class TrackRobot(robot_control.Robot_Control):

	def __init__(self):
		self.leftSensor = optical_sensor.Optical_Sensor(6)
		self.rightSensor = optical_sensor.Optical_Sensor(13)
		self.status = "stopped"
		self.direction = 0.4

		self.x_pin = 5
		self.y_pin = 6

		self.x_pan = sc(5)
		self.y_pan = sc(6)

		self.x = [90, 120, 150, 170, 150, 120, 90, 50, 30, 10, 30, 50]
		self.y = [90, 120, 150, 170, 150, 120, 90]



	def checkTrack(self):

			rightVal = self.leftSensor.read_sensor()
			leftVal = self.rightSensor.read_sensor()

			goStraight = rightVal and leftVal

			if goStraight(self):
				if self.direction == 1:
					self.goStraight()
				else:
					self.goBack()
				if not self.status == "moving":
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
			for x in self.x:
				self.x_pan.change_angle(x)
				currenttime = time.perf_counter()
				while time.perf_counter() - currenttime < 1:
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
	    
            Robot.scan()

    except KeyboardInterrupt:
        GPIO.cleanup() 
        pass
