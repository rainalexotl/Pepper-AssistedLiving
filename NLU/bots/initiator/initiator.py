from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources
import requests
import sys

sys.path.append("...")
from initiator_responder import initiator_responder

matchmaking_strings = {"greet", "bye", "thank", "affirm"}

class initiator():
    def __init__(self, responder):
        print('[BOTS/INITIATOR] Starting...')

        self.responder = responder

        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/initiator/std-startup.xml")
        self.aiml.respond("load aiml b")

        self.initiator_responder = initiator_responder(responder)

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

        print('[BOTS/INITIATOR] Routing:', responder)

        if responder == "initiator_request_forename_1":
            self.initiator_request_forename_1()
            return self.lockcode, 0, self.forename_1, self.forename_2
        elif responder == "initiator_get_forename_1":
            self.initiator_get_forename_1()
            return self.lockcode, 0, self.forename_1, self.forename_2
        elif responder == "initiator_get_forename_1_and_forename_2":
            self.initiator_get_forename_1_and_forename_2()
            return -1, 0, self.forename_1, self.forename_2
        elif responder == "initator_enter_individual_mode":
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
            response = "Sorry, I didn't quite get that. Can you repeat that?"
            self.responder.respond(response)
            print('[BOTS/INITIATOR] Invalid responder value. Check bots/initiator/aiml/initiator.aiml')
            return -1, 0, self.forename_1, self.forename_2

    def initiator_request_forename_1(self):
        self.initiator_responder.responder_request_forename_1()

    def initiator_get_forename_1(self):
        self.aiml.respond(self.utterance)
        self.forename_1 = self.aiml.getPredicate('forename_1')

        self.responder.setNames(self.forename_1, self.forename_2)

        self.initiator_responder.responder_get_forename_1()

        self.checkPerson(self.forename_1)

    def initiator_get_forename_1_and_forename_2(self):
        self.aiml.respond(self.utterance)
        self.forename_1 = self.aiml.getPredicate('forename_1')
        self.forename_2 = self.aiml.getPredicate('forename_2')

        self.responder.setNames(self.forename_1, self.forename_2)

        self.initiator_responder.responder_get_forename_1_and_forename_2()

    def initator_enter_individual_mode(self):
        response = "No? Ok, lets see what the two of us can talk about."
        self.responder.respond(response)

    def initiator_request_forename_2(self):
        response = "Ok. Who is it that is with you?"
        self.responder.respond(response)
        
    def initiator_get_forename_2(self):
        self.aiml.respond(self.utterance)
        self.forename_2 = self.aiml.getPredicate('forename_2')

        self.responder.setNames(self.forename_1, self.forename_2)

        response = "Ok, I will be glad to talk to you and " + self.forename_2
        self.responder.respond(response)

    def checkPerson(self, forename):
        url = "http://localhost:3000/api/person/add/person"

        payload = "forename=" + forename + "&surname=unknown"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "cb84a184-2e07-4769-b09a-6fd09a1658d3"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        response = json.loads(str(response.text))