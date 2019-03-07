import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 3003)
print ('[CLIENT_SIMULATE] Connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    while True:
        message = raw_input("Utterance: ")
        sock.sendall(message)

finally:
    print('[CLIENT_SIMULATE] Closing socket...')
    sock.close()