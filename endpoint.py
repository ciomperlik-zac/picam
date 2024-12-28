import socket

ip = socket.gethostbyname(socket.gethostname())

print(f"Pi Cam Endpoint\n\nIP: {ip}\n")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, 11000))
server.listen()

def callback(msg):
    pass

while True:
    client, addr = server.accept()
    print("> Client connected")

    while True:
        msg = client.recv(1024).decode("utf-8")
        
        if not msg:
            break
        else:
            print(">", msg)

            callback(msg)

    print("> Client disconnected")
    client.close()
