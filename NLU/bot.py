from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer, Metadata, Interpreter
from rasa_nlu import config

from bots.initiator import initiator
from bots.matchmaking import matchmaking
# from bots.calendar import calendar
# from bots.recall import recall
# from bots.confluence import confluence

from responder import responder

import json
import socket
import sys
import requests
import random 

initiator_strings   = {"greet", "thank", "affirm"}
matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}
calendar_strings    = {"calendar_events_today", "calendar_upcoming_visitors", "calendar_event_search_doctor",
                        "calendar_event_search_bingo", "calendar_event_search_lunch", "calendar_event_search_dinner",
                        "calendar_event_search_film", "calendar_event_friend_today"}
recall_strings      = {"recall_start", "recall_escape"}
confluence_strings  = {}
reset_strings = {"bye"}

class bot:
    def __init__(self):
        self.lock = 0 # 0 directs to initator, -1 will unlock

        self.interpreter = Interpreter.load('./models/default')

        self.matchmaking = matchmaking.matchmaking()
        self.initiator = initiator.initiator()

        self.responder = responder()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_address = ('localhost', 3200)
        print('[PRIMARY BOT] Starting up on %s port %s' % self.server_address)
        self.sock.bind(self.server_address)

        self.forename_1 = ''
        self.forename_2 = ''

        self.mode = 0

        self.init = 1

    def train (self, data, config_file, model_dir):
        training_data = load_data(data)
        configuration = config.load(config_file)
        trainer = Trainer(configuration)
        trainer.train(training_data)
        #model_directory = trainer.persist(model_dir, fixed_model_name = 'chat')

    def run(self):
        self.sock.listen(1)

        while True:
            print('[PRIMARY BOT] Waiting for request...')
            self.connection, self.client_address = self.sock.accept()
            try:
                print('[PRIMARY BOT] Connection from: ', self.client_address)

                while True:
                    data = self.connection.recv(256)
                    if data:
                        self.parse(data)
                    else:
                        break             
            finally:
                self.connection.close()
                print('[PRIMARY BOT] Connection closed.')

    def parse(self, text):
        unicodedString = unicode(text, "utf-8")

        result = self.interpreter.parse(unicodedString)

        if result["text"] == "@SHUTDOWN@":
            self.shutdown()

        self.routing(result, 0)

    def routing(self, result, internal):
        if internal == 1:
            intent = 'null'
            intent_name = 'null'
            intent_conf = 'null'
            utterance = result
        else:
            intent = result["intent"]
            intent_name = intent["name"]
            intent_conf = intent["confidence"]
            utterance = result["text"]

            print('Utterance:', utterance)

            print('')
            print('*** INTENT ***')
            print('Intent: ', intent_name)
            print('Conf.: ', intent_conf)

        if self.lock == -1:
            print('[PRIMARY BOT] Using intent to select appropriate bot...')
        else:
            print('[PRIMARY BOT] Conversation is locked. Intent ignored.')
        print('')
            
        if intent_name in reset_strings:
            self.reset()
            return

        if self.init == 1:
            print('[PRIMARY BOT][INIT] Selecting... Bot 0: Initiator')
            self.lock, self.mode, self.forename_1, self.forename_2 = self.initiator.check(intent_name, utterance)
            if self.lock == -1 and self.mode == 1:
                self.init = 0
                self.routing('init matchmaking', 1)
        else:
            if self.mode == 1:
                if self.lock == -1:
                    if intent_name in initiator_strings:
                        print('[PRIMARY BOT] Selecting... Bot 0: Initiator')
                        self.lock, self.mode, self.forename_1, self.forename_2 = self.initiator.check(intent_name, utterance)
                    elif intent_name in matchmaking_strings or utterance == 'init matchmaking':
                        if utterance == 'init matchmaking':
                            print('[PRIMARY BOT] Selecting... Bot 1: Matchmaking')
                            self.lock = self.matchmaking.check(intent_name, utterance, self.forename_1, 1)
                        else:
                            print('[PRIMARY BOT] Selecting... Bot 1: Matchmaking')
                            self.lock = self.matchmaking.check(intent_name, utterance, self.forename_1, 0)
                else:
                    if self.lock == 0:
                        self.lock, self.mode, self.forename_1, self.forename_2 = self.initiator.check(intent_name, utterance)
                    elif self.lock == 1:
                        self.lock = self.matchmaking.check(intent_name, utterance, self.forename_1, 0)
            elif self.mode == 2:
                print('[PRIMARY BOT] Selecting... Bot 4: Confluence')
                #self.lock = self.confluence.check(intent_name, utterance)

        print('')

    def reset(self):
        self.lock = 0 # 0 directs to initator, -1 will unlock

        self.interpreter = Interpreter.load('./models/default')

        self.matchmaking = matchmaking.matchmaking()
        self.initiator = initiator.initiator()

        self.responder = responder()

        self.forename_1 = ''
        self.forename_2 = ''

        self.mode = 0

        self.init = 1

    def shutdown(self):
        print('[PRIMARY BOT] Shutting down...')

        self.connection.close()

        url = "http://localhost:3000/api/person/shutdown"

        payload = "command=SHUTDOWN"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "aac3ca7d-400c-41f6-a1dc-0f660364ffcf"
            }

        requests.request("POST", url, data=payload, headers=headers)

        self.responder.shutdown()

        print('[PRIMARY BOT] Goodbye.')

        raise SystemExit

foo = bot()
foo.run()