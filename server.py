import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.settimeout(5)
server.bind(('', 5000))

def factorial(num):
    res = 1
    for i in range(1, num+1):
        res*=i
    return res

print("Initiating server")
server.listen()
conn_obj, client_addr = server.accept()
print(str(client_addr) +" connected")
format = 'utf-8'
while True:
    msg_len = conn_obj.recv(64).decode(format)
    if msg_len:
        msg_len = int(msg_len)
        msg = conn_obj.recv(msg_len).decode(format)
        if msg == "##close_connection##":
            break
        try:
            res = factorial(int(msg))
        except ValueError:
            res = 'Please send a number to calculate factorial'
        print("Received "+msg+" from "+str(client_addr))
        conn_obj.send(str(res).encode(format))

print("Connection closed by "+str(client_addr))
conn_obj.send("Connection Closed".encode(format))
conn_obj.close()
