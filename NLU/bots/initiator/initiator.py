from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources
import requests

matchmaking_strings = {"greet", "bye", "thank", "affirm"}

class initiator():
    def __init__(self):
        print('[BOTS/INITIATOR] Starting...')

        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/initiator/std-startup.xml")
        self.aiml.respond("load aiml b")

        self.utterance = ''
        self.mode = 0
        self.forename_1 = 'unknown'
        self.forename_2 = 'unknown'

        self.lockcode = 0

    def check(self, intent, utterance):
        print('[BOTS/INITIATOR] Responding...')

        self.utterance = utterance

        self.aiml.respond(self.utterance)
        responder = self.aiml.getPredicate('responder')

        print(responder)

        if responder == "initiator_request_forename_1":
            self.initiator_request_forename_1()
            return self.lockcode, 0, self.forename_1, self.forename_2
        elif responder == "initiator_get_forename_1":
            self.initiator_get_forename_1()
            return self.lockcode, 0, self.forename_1, self.forename_2
        elif responder == "enter_individual_mode":
            self.initator_enter_individual_mode()
            return -1, 1, self.forename_1, self.forename_2
        elif responder == "initiator_request_forename_2":
            self.initiator_request_forename_2()
            return self.lockcode, 0, self.forename_1, self.forename_2
        elif responder == "initiator_get_forename_2":
            self.initiator_get_forename_2()
            return -1, 2, self.forename_1, self.forename_2
        elif responder == "initator_unlock_conversation":
            return -1, 0, self.forename_1, self.forename_2
        else:
            print('[BOTS/INITIATOR] Invalid responder value. Check bots/initiator/aiml/initiator.aiml')
            return -1, 0, self.forename_1, self.forename_2

    def initiator_request_forename_1(self):
        print("Hi there, who am I talking with?")

    def initiator_get_forename_1(self):
        self.aiml.respond(self.utterance)
        self.forename_1 = self.aiml.getPredicate('forename_1')

        print('Ok, ', self.forename_1, ' is there anyone else there with you?')

    def initator_enter_individual_mode(self):
        print('No? Ok, lets see what the two of us can talk about.')

    def initiator_request_forename_2(self):
        print('Ok. Who is it that is with you?')
        
    def initiator_get_forename_2(self):
        print('Ok, ill be glad to talk to both of you.')

        self.aiml.respond(self.utterance)
        self.forename_2 = self.aiml.getPredicate('forename_2')