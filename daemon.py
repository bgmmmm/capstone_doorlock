import gpiozero as gpio
from sensor_module import *
from face_module import *
from bluetooth import *


blue = gpio.LED(25)
red = gpio.LED(5)


client_socket = BluetoothSocket(RFCOMM)
client_socket.connect(("00:21:11:01:79:47",1))


while True:
    if (read_spi_adc() > 200):        
        emergency_open() #if adcValue > 200 (fire)

    if motion_detect():
        print("motion detected!")
        blue.blink()
        if face_recognition == True:
            blue.off()
            blue.on()
            door_open()   
            time.sleep(10)
            blue.off()
            
        else:
            blue.off()
            red.on()
            time.sleep(2)
            red.off()
        
    else:
        client_socket.settimeout(1)
        try:
            msg = client_socket.recv(1024)
            msg = msg.decode('utf-8')

            if msg == "1": 
                print("correct password")
                blue.on()
                door_open()
                blue.off()


            elif msg == "2":
                print("adding face")
                with open("/home/user/Desktop/face_id.txt", "r") as f:
                    face_id = int(f.read())

                if (face_id > 0) & (face_id <= 10):
                    blue.on()
                    face_add(face_id)
                    print("face added")
                    face_training()
                    blue.off()
                   

                else:
                    print("[WARNING] no more adding!")
                    red.on()
                    time.sleep(2)
                    red.off()
                   
    
            elif msg=="3":
                print("3")
                remove_all()
        except BaseException:
            continue