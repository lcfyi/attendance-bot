import robot_control
import optical_sensor
import time

class TrackRobot(robot_control.Robot_Control):

	def __init__(self):
		self.leftSensor = optical_sensor.Optical_Sensor(6)
		self.rightSensor = optical_sensor.Optical_Sensor(13)
		self.status = "stopped"
		self.direction = 1


	def checkTrack(self):
		rightVal = self.leftSensor.read_sensor()
		leftVal = self.rightSensor.read_sensor()

		goStraight = rightVal and leftVal

		if goStraight(self, direction):
			if direction == 1:
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
            	Robot.goStraight(Robot.direction)

    except KeyboardInterrupt:
        GPIO.cleanup() 
        pass