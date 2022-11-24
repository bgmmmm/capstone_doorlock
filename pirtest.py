import gpiozero as gpio

pir = gpio.MotionSensor(26)

while True:
    if pir.motion_detected:
        print("motion detected")
    else:
        print("no motion")
