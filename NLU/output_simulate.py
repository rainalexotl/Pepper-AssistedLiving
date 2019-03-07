import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 4000)
sock.bind(server_address)

sock.listen(1)

print('[OUTPUT_SIMULATE] Waiting...')

while True:
    connection, client_address = sock.accept()
    try:
        print('[OUTPUT_SIMULATE] Connection from: ', client_address)

        while True:
            data = connection.recv(64)
            if data:
                print(data)
            else:
                break             
    finally:
        connection.close()
        print('[PRIMARY BOT] Connection closed.')