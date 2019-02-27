from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer, Metadata, Interpreter
from rasa_nlu import config

# from bots.chit_chat import chit_chat
from bots.matchmaking import matchmaking
# from bots.calendar import calendar
# from bots.recall import recall

import json
import socket
import sys

chit_chat_strings   = {"greet", "thank", "affirm", "bye"}
matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}
calendar_strings    = {"calendar_events_today", "calendar_upcoming_visitors", "calendar_event_search_doctor",
                        "calendar_event_search_bingo", "calendar_event_search_lunch", "calendar_event_search_dinner",
                        "calendar_event_search_film", "calendar_event_friend_today"}
recall_strings      = {"recall_start", "recall_escape"}

class bot:
    def __init__(self):
        self.lock = -1

        self.interpreter = Interpreter.load('./models/default')
        self.matchmaking = matchmaking.matchmaking()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_address = ('localhost', 3002)
        print('[PRIMARY BOT] Starting up on %s port %s' % self.server_address)
        self.sock.bind(self.server_address)

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
                    data = connection.recv(16)
                    if data:
                        self.parse(data)
                    else:
                        break             
            finally:
                connection.close()
                print('[PRIMARY BOT] Connection closed.')

    def parse(self, text):
        unicodedString = unicode(text, "utf-8")

        if self.lock == -1:
            result = self.interpreter.parse(unicodedString)
        else:
            result = unicodedString

        self.routing(result)

    def routing(self, result):
        intent = result["intent"]
        intent_name = intent["name"]
        intent_conf = intent["confidence"]

        print('')
        print('*** INTENT ***')
        print('Intent: ', intent_name)
        print('Conf.: ', intent_conf)
        print('')
            
        if self.lock == -1:
            if intent_name in chit_chat_strings:
                print('Selecting... Bot 0: Chit Chat')
                #self.lock = self.chit_chat.check(intent_name)
            elif intent_name in matchmaking_strings:
                print('Selecting... Bot 1: Matchmaking')
                self.lock = self.matchmaking.check(intent_name)
            elif intent_name in calendar_strings:
                print('Selecting... Bot 2: Calendar')
                #self.lock = self.calendar.check(intent_name)
            elif intent_name in recall_strings:
                print('Selecting... Bot 3: Recall Quiz')
                #self.lock = self.recall.check(intent_name)
        else:
            if self.lock == 1:
                self.matchmaking.check(intent_name)
            # if self.lock == 0:
            #     self.chit_chat.check(intent_name)
            # elif self.lock == 1:
            #     self.matchmaking.check(intent_name)
            # elif self.lock == 2:
            #     self.calendar.check(intent_name)
            # elif self.lock == 3:
            #     self.recall.check(intent_name)

        print('')

foo = bot()
foo.run()