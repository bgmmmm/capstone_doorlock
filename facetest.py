import time
from sensor_module import *
from face_module import *

red = gpio.LED(5)
blue = gpio.LED(25)

while True:
    if motion_detect():
        with open("face_id.txt", "r") as f:
            face_id = int(f.read())

        if (face_id > 0) & (face_id <= 10):
            blue.on()
            face_add(face_id)         
            print("face added!")
            face_training()
            blue.off()
        else:
            print("no more adding!")
            red.on()
            time.sleep(2)
            red.off()
    else:
        print("no motion!")
        time.sleep(1)
