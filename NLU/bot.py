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

import json
import socket
import sys
import random

initiator_strings   = {"greet", "thank", "affirm", "bye"}
matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}
calendar_strings    = {"calendar_events_today", "calendar_upcoming_visitors", "calendar_event_search_doctor",
                        "calendar_event_search_bingo", "calendar_event_search_lunch", "calendar_event_search_dinner",
                        "calendar_event_search_film", "calendar_event_friend_today"}
recall_strings      = {"recall_start", "recall_escape"}
confluence_strings  = {}

class bot:
    def __init__(self):
        self.lock = 0 # 0 directs to initator, -1 will unlock

        self.interpreter = Interpreter.load('./models/default')

        self.matchmaking = matchmaking.matchmaking()
        self.initiator = initiator.initiator()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_address = ('localhost', 3030)
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
            connection, client_address = self.sock.accept()
            try:
                print('[PRIMARY BOT] Connection from: ', client_address)

                while True:
                    data = connection.recv(64)
                    if data:
                        self.parse(data)
                    else:
                        break             
            finally:
                connection.close()
                print('[PRIMARY BOT] Connection closed.')

    def parse(self, text):
        unicodedString = unicode(text, "utf-8")

        result = self.interpreter.parse(unicodedString)

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
            
        if self.init == 1:
            print('[PRIMARY BOT][INIT] Selecting... Bot 0: Initiator')
            self.lock, self.mode, self.forename_1, self.forename_2 = self.initiator.check(intent_name, utterance)
            if self.lock == -1:
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

foo = bot()
foo.run()