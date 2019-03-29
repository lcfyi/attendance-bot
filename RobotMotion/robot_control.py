import time
from adafruit_motorkit import MotorKit

#inherited by robot to control over tracks, only need 90 degree turns
class Robot_Control:

	straight_val = 0.4
	kit = MotorKit()
	left_wheel = kit.motor2
	right_wheel = kit.motor1
	left_throttle = 0
	right_throttle = 0

	def turnLeftImm(self):

		self._setLeft(0)
		self._setRight(-1 * self.straight_val)

	def turnRightImm(self):

		self._setLeft(self.straight_val)
		self._setRight(0)

	def goStraight(self):
		self._setLeft(self.straight_val)
		self._setRight(-1 * self.straight_val)

	def goBack(self):
		self._setLeft(-1 * self.straight_val)
		self._setRight(self.straight_val)

	def stop(self):
		self._setLeft(0)
		self._setRight(0)
	
	def changeSpeed(self, speed = 0.4):
		if speed >= 0 and speed <=0.8:
			Robot_Control.straight_val = speed

	def _setLeft(self, val):

		try:
			if val != self.left_wheel.throttle:
				self.left_wheel.throttle = val
				self.left_throttle = self.left_wheel.throttle

		except:
			pass

	def _setRight(self, val):

		try:
			if val != self.right_wheel.throttle:
				self.right_wheel.throttle = val
				self.right_throttle = self.right_wheel.throttle

		except:
			pass

