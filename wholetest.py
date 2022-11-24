import gpiozero as gpio
import time
from face_module import *
from sensor_module import *

blue = gpio.LED(25)
red = gpio.LED(5)

while True:
    if motion_detect():
        blue.blink()
        avg = face_recognition()
        blue.off()
        if avg >= 50:
            blue.on()
            door_open()
            blue.off()
        else:
            red.on()
            time.sleep(2)
            red.off()
        break
    else:
        print("no motion")
        time.sleep(1)
