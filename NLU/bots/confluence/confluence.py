from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources
import random
import requests

from confluence_responder import confluence_responder

confluence_strings  = {}

#we should know the forenames of both personel at this point in the program

class confluence():
    def __init__(self, responder):
        print('[BOTS/CONFLUENCE] Starting...')

        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/confluence/std-startup.xml")
        self.aiml.respond("load aiml b")

        self.aiml_affirm = aiml.Kernel()
        self.aiml_affirm.learn("bots/confluence/std-startup-affirm.xml")
        self.aiml_affirm.respond("load aiml b")

        self.responder = responder
        self.confluence_responder = confluence_responder(responder)

        self.utterance = ''
        self.forename_1, self.forename_2 = self.responder.getNames()
        
        self.affirmStatus = 0
        self.affirmCaller = ""
        self.affirm = 0

        self.usedCommonLikes = []
        self.stackLikes = []

        self.lockcode = 2

    def check(self, intent, utterance, driver):
        print('[BOTS/CONFLUENCE] Responding...')

        self.forename_1, self.forename_2 = self.responder.getNames()

        self.utterance = utterance

        self.aiml.respond(self.utterance)
        responder = self.aiml.getPredicate('responder')
        
        if driver == 1:
            responder = "confluence_initiate_introduction"

        if self.affirmStatus == 1:
            responder = self.affirmCheck()

        if responder == "confluence_initiate_introduction":
            self.confluence_initiate_introduction()
            return self.lockcode
        elif responder == "confluence_initiate_confirm":
            lock = self.confluence_initiate_confirm()
            return lock
        elif responder == "confluence_confirm_topic_choice":
            lock = self.confluence_confirm_topic_choice()
            return lock
        elif responder == "confluence_initiate_conversation":
            self.confluence_initiate_conversation()
            return self.lockcode
        elif responder == "confluence_new_topic_of_conversation":
            self.confluence_new_topic_of_conversation()
            return self.lockcode
        elif responder == "confluence_topic_end":
            lock = self.confluence_topic_end()
            return lock
        elif responder == "confluence_leave_conversation":
            self.confluence_leave_conversation()
            return -1

    def confluence_initiate_introduction(self):
        self.affirmCaller = "confluence_initiate_introduction"
        self.affirmStatus = 1
        self.confluence_responder.responder_initiate_introduction()

    def confluence_initiate_confirm(self):
        if self.affirm == 1:
            self.populateCommonLikes()
            self.confluence_initiate_conversation()
            return self.lockcode
        else:
            response = "No worries, I will be here if you need me."
            self.responder.respond(response)
            return -1

    def populateCommonLikes(self):
        self.responder.setNames(self.forename_1, self.forename_2)

        url = "http://localhost:3000/api/person/commonlikes"

        payload = "forename_1=" + self.forename_1 + "&forename_2=" + self.forename_2 + "&type=specific_friend"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "5777f647-b96b-4f17-8d71-906e1e3ae6b2"
        }

        likes = requests.request("POST", url, data=payload, headers=headers)
        likes = json.loads(str(likes.text))

        for i in range(0, len(likes["commonLikes"])-1):
            self.stackLikes.append(likes["commonLikes"][i])

    def confluence_initiate_conversation(self):
        if self.stackLikes:
            commonLike = self.stackLikes.pop()
            self.confluence_responder.responder_initiate_conversation(commonLike)
        else:
            response = "Sorry, I can't think of anything else for you to talk about. Try adding more likes to your profiles."
            self.responder.respond(response)

        self.affirmCaller = "confluence_initiate_conversation"
        self.affirmStatus = 1

    def confluence_confirm_topic_choice(self):
        if self.affirm == 1:
            self.stackLikes = []
            self.confluence_topic_confirmed()
            return self.lockcode
        else:
            self.confluence_initiate_conversation()
            return -1

    # Change this so that it offers to tell more about common like first
    def confluence_topic_confirmed(self):
        response = "Ok, I will leave you two to chat. Let me know when you are done."
        self.responder.respond(response)

        self.affirmCaller = "confluence_topic_confirmed"
        self.affirmStatus = 1

    def confluence_topic_end(self):
        if self.affirm == 1:
            self.confluence_initiate_conversation()
            return self.lockcode
        else:
            self.confluence_topic_confirmed()
            return self.lockcode

    def confluence_new_topic_of_conversation(self):
        self.confluence_responder.responder_new_topic_of_conversation()

    def confluence_leave_conversation(self):
        self.confluence_responder.responder_leave_conversation()

    def affirmCheck(self):
        self.aiml_affirm.respond(self.utterance)
        predicate = self.aiml_affirm.getPredicate('affirm')

        if predicate == "YES":
            print('Affirm: YES')
            affirm = 1
        elif predicate == "NO":
            print('Affirm: NO')
            affirm = 0
        else:
            self.affirmStatus = 0
            self.check('', '', 1)
            affirm = -1

        if self.affirmCaller == "confluence_initiate_introduction":
            target = "confluence_initiate_confirm"
        elif self.affirmCaller == "confluence_initiate_conversation":
            target = "confluence_confirm_topic_choice"
        elif self.affirmCaller == "confluence_topic_confirmed":
            target = "confluence_topic_end"
        else:
            target = 'null'

        self.affirm = affirm
        self.affirmStatus = 0

        return target