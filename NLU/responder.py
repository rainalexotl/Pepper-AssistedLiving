import json
import socket
import sys
import requests
import random
import time
import datetime
import os
import pyttsx

class responder:
    def __init__(self):
        print('[RESPONDER] Responder is starting...')

        # self.engine = pyttsx.init()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('192.168.2.76', 4000) # Change to Alana response input
        # self.server_address = ('localhost', 4000) # Change to Alana response input
        try:
            self.sock.connect(self.server_address)
            print('[RESPONDER] Successfully connected to Alana.')
        except Exception as ex:
            print('[RESPONDER] Unable to connect to Alana.', ex)

        self.forename_1 = ''
        self.forename_2 = ''

    def respond(self, response):
        try:
            print('[RESPONDER]', response)
            self.sock.sendall(response)
            self.log(response)
            # self.engine.say(response)
            # self.engine.runAndWait()
        except:
            print('[RESPONDER] Socket connection exception. Unable to connect to Alana.')

    def handoff(self, topic):
        print('[RESPONDER] Handing off topic', topic, 'to Alana...')

    def setNames(self, forename_1, forename_2):
        self.forename_1 = forename_1
        self.forename_2 = forename_2

    def getNames(self):
        return self.forename_1, self.forename_2

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