import RPi.GPIO as GPIO
import time 

# Object for our optical sensor
class Optical_Sensor:
    def __init__(self, sensor):
        self.sensor = sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Return the inverse value, just for better readability
    def read_sensor(self):
        return not GPIO.input(self.sensor)