import socket
import threading
import time

server_ips = []
monitor_ip = '192.168.122.1'

thread_exec = True
base = 30000
sleep_time = 1

def msg_len(msg):
    send_len = str(len(msg)).encode('utf-8')
    send_len+= b' ' * (64-len(send_len))
    return send_len

def connect_monitor():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((monitor_ip,5050))
    global thread_exec

    while thread_exec:
        msg=''
        format = 'utf-8'
        if len(server_ips)==0:
            #print("Server IP list empty. Fetching IP...")
            msg = "fetchIP".encode(format)
            client.send(msg)
            ip = client.recv(1024).decode(format)
            server_ips.append(ip)

        msg="cpu".encode(format)
        client.send(msg)
        ip = client.recv(1024).decode(format)
        if ip:
            server_ips.append(ip)
            break

def connect_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global thread_exec
    global num
    global sleep_time
    while thread_exec:
        format = 'utf-8'
        for x in range(len(server_ips)):
            num = str(base).encode(format)
            #print("Sending request to IP "+server_ips[x])
            client.sendto(msg_len(num),(server_ips[x],5000))
            client.sendto(num,(server_ips[x],5000))
            time.sleep(sleep_time)


def interface():
    global thread_exec
    global base
    while thread_exec:
        msg = input("Client> ")
        if msg == '##end##':
            thread_exec = False
        elif msg == "high_load":
            base = 46000
        elif msg == "low_load":
            base = 30000



monitor_conn_thread = threading.Thread(target=connect_monitor,daemon=True)
monitor_conn_thread.start()

client_interface_thread = threading.Thread(target=interface,daemon=True)
client_interface_thread.start()

server_conn_thread = threading.Thread(target=connect_server,daemon=True)
server_conn_thread.start()

monitor_conn_thread.join()
client_interface_thread.join()
server_conn_thread.join()
