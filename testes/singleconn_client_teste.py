import socket
import time
import random

HOST = 'localhost'  # The server's hostname or IP address
PORT = 5000        # The port used by the server

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
random_number = random.randint(0,1000)
while True:
  socket.sendall(f'{random_number}'.encode())
  data = socket.recv(1024)
  print('Received', repr(data))
  time.sleep(1)
