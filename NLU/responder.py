import json
import socket
import sys
import requests
import random

class responder:
    def __init__(self):
        print('[RESPONDER] Responder is starting...')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_address = ('localhost', 4000) # Change to Alana response input
        try:
            self.sock.connect(self.server_address)
            print('[RESPONDER] Successfully connected to Alana.')
        except:
            print('[RESPONDER] Unable to connect to Alana.')

    def respond(self, response):
        try:
            self.sock.sendall(response)
        except:
            print('[RESPONDER] Socket connection exception. Unable to connect to Alana.')

    def shutdown(self):
        print('[RESPONDER] Shutting down...')
        self.sock.close()