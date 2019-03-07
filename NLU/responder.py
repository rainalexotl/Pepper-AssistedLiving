import json
import socket
import sys
import requests
import random

class responder:
    def __init__(self):
        print('[RESPONDER] Responder is starting...')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_address = ('localhost', 3004) # Change to Alana response input
        self.sock.connect(self.server_address)

    def respond(self, response):
        try:
            self.sock.sendall(response)
        except:
            print('[RESPONDER] Socket connection exception. Unable to connect to Alana.')

    def shutdown(self):
        print('[RESPONDER] Shutting down...')
        self.sock.close()