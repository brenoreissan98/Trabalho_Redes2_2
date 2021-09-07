"""
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket.bind((HOST, PORT))
socket.listen(10)
socket.setblocking(False)
while True:
  conn, addr = socket.accept()
  print('Connected by', addr)
  data = conn.recv(1024)
  if not data:
      break
  conn.sendall(data)
  print("Travei?")
"""

import select
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 5000))
server_socket.listen(10)
print("Listening on port 5000")

read_list = [server_socket]
while True:
  readable, writable, errored = select.select(read_list, [], [])
  for s in readable:
    if s is server_socket:
        client_socket, address = server_socket.accept()
        read_list.append(client_socket)
        print("Connection from", address)
    else:
        data = s.recv(1024)
        if data:
            s.send(data)
        else:
            s.close()
            print("removi", s)
            read_list.remove(s)