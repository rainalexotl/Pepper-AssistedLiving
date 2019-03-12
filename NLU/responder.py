import json
import socket
import sys
import requests
import random
import time
import datetime
import os

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
            self.log(response)
        except:
            print('[RESPONDER] Socket connection exception. Unable to connect to Alana.')

    def handoff(self, topic):
        print('[RESPONDER] Handing off topic', topic, 'to Alana...')

    def shutdown(self):
        print('[RESPONDER] Shutting down...')
        self.sock.close()

    def log(self, response):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        logString = '[' + st + '] [RESPONSE] ' + response + '\n'

        f = open('log.txt', 'a', os.O_NONBLOCK)
        f.write(logString)
        f.flush()
        f.close()