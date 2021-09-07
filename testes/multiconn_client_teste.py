import selectors
import socket
import types
import selectors
import types

sel = selectors.DefaultSelector()

host = "localhost"
port = 5000

server_addr = (host, port)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('starting connection', 'to', server_addr)
sock.connect_ex(server_addr)
sock.setblocking(False)

def start_connections(host, port, num_conns):
    for i in range(0, num_conns):
        connid = i + 1
        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        messages = f"MESSAGE {connid}"

        data = types.SimpleNamespace(connid=connid,
                                    msg_total=1,
                                    recv_total=0,
                                    messages=messages,
                                    outb=b'')
        sel.register(sock, events, data=data)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print('received', repr(recv_data), 'from connection', data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print('closing connection', data.connid)
            sel.unregister(sock)
            #sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print('sending', repr(data.outb), 'to connection', data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

# ...

start_connections(host, port, 5)

while True:
  events = sel.select(timeout=None)
  for key, mask in events:
      if key.data is None:
          accept_wrapper(key.fileobj)
      else:
          service_connection(key, mask)
