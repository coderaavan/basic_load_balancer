import socket
import threading
import time

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 5000))

def factorial(num):
    res = 1
    for i in range(1, num+1):
        res*=i
    return res

while True:
    format = 'utf-8'
    msg_len, client_addr = server.recvfrom(64)
    msg_len = msg_len.decode(format)
    if msg_len:
        msg_len = int(msg_len)
        msg, client_addr = server.recvfrom(msg_len)
        msg = msg.decode(format)
        res = factorial(int(msg))
