import gpiozero as gpio
import spidev
import time

def door_open():
    servo = gpio.AngularServo(21, min_pulse_width=0.0005, max_pulse_width=0.00255)
    servo.angle = -90
    time.sleep(10.0)
    servo.angle = 0
    time.sleep(2)
    servo.angle = -90


def emergency_open():
    servo = gpio.AngularServo(21, min_pulse_width=0.0005, max_pulse_width=0.00255)
    servo.angle = -90
    time.sleep(180.0)
    servo.angle = 0
    time.sleep(2)
    servo.angle = -90



def motion_detect():
    pir = gpio.MotionSensor(26)
    
    if pir.motion_detected:
        return True
    else:
        return False


def read_spi_adc():

    spi = spidev.SpiDev()
    spi.open(0,0)
    spi.max_speed_hz = 500000
    adcChannel = 0
    adcValue = 0
    buff = spi.xfer2([1,(8+adcChannel)<<4,0])
    adcValue = ((buff[1]&3)<<8)+buff[2]		
    spi.close()

    return adcValue 

