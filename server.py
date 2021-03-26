import socket
import threading

host_ip =  socket.gethostbyname(socket.gethostname())
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host_ip, 5000))

def factorial(num):
    res = 1
    for i in range(1, num+1):
        res*=i
    return res

def new_client(conn_obj, client_addr):
    print(str(client_addr) +" connected")
    format = 'utf-8'
    while True:
        msg_len = conn_obj.recv(64).decode(format)
        if msg_len:
            msg_len = int(msg_len)
            msg = conn_obj.recv(msg_len).decode(format)
            res = factorial(int(msg))
            if msg == "##close_connection##":
                break
            print("Received "+msg+" from "+str(client_addr))
            conn_obj.send(str(res).encode(format))

    print("Connection closed by "+str(client_addr))
    conn_obj.send("Connection Closed".encode(format))
    conn_obj.close()


def initiate_server():
    server.listen()
    print("Server is listening on "+host_ip)
    while True:
        conn_obj, client_addr = server.accept()
        thread = threading.Thread(target=new_client, args=(conn_obj, client_addr))
        thread.start()
        print("Active connections are "+str(threading.activeCount()-1))


print("Initiating server")
initiate_server()
