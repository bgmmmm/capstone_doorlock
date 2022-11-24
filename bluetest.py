from bluetooth import *

# Create the client socket
client_socket=BluetoothSocket(RFCOMM)
client_socket.connect(("00:21:11:01:79:47", 1))

while True:
    msg = client_socket.recv(1024)
    print("received message : {}".format(msg))

print("Finished")
client_socket.close()
