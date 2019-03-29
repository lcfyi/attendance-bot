import pigpio
import time

# Servo control class, using pigpio as our GPIO PWM controller
class Servo_Control:
    def __init__(self, servo):
        # Uses the existing pigpio daemon running on system
        # If error, run sys command "sudo pigpiod"
        self.pig = pigpio.pi()
        # Set frequency to 50hz
        self.pig.set_PWM_frequency(servo, 50)
        # Set our pins and angle
        self.servo = servo
        self.angle = 90
        # Reset to 90 degrees
        self.reset()

    # Gets the angle
    def get_angle(self):
        return self.angle 

    # Changes the angle based on delta to previous value
    def change_angle_delta(self, delta):
        if self.angle - delta < 170 and self.angle - delta > 10:
            self.change_angle(self.angle - delta)

    # Sets the angle of the servo to the parameter
    def change_angle(self, angle):
        self.angle = angle
        self.pig.set_PWM_dutycycle(self.servo, (((angle / 180.0) * 2.0 + 0.4) / 20.0) * 255.0)

    # Resets the servo position
    def reset(self):
        self.change_angle(90)