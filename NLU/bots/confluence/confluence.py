from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources
import requests

from confluence_responder import confluence_responder

confluence_strings  = {}

#we should know the forenames of both personel at this point in the program

class confluence():
    def __init__(self):
        print('[BOTS/CONFLUENCE] Starting...')

        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/confluence/std-startup.xml")
        self.aiml.respond("load aiml b")

        self.confluence_responder = confluence_responder()

        self.utterance = ''
        self.forename_1 = '' #known forenames
        self.forename_2 = ''
        self.common_interest1 = 'unknown'
        self.common_interest2 = 'unknown'

        self.lockcode = 0

    def check(self, intent, utterance):
        print('[BOTS/CONFLUENCE] Responding...')

        self.utterance = utterance

        self.aiml.respond(self.utterance)
        responder = self.aiml.getPredicate('responder')

        print(responder)
            
        if responder == "initiate_introduction":
            self.initiate_introduction()
        elif responder == "profile_match_both_people": #ronnie has matchmake made - check.
            self.profile_match_both_people()
        elif responder == "initiate_conversation":
            self.initiate_conversation()
        elif responder == "new_topic_of_conversation":
            self.new_topic_of_conversation()
        elif responder == "leave_conversation":
            self.leave_conversation()

    def initiate_introduction(self):
        self.confluence_responder.responder_initiate_introduction()

    def profile_match_both_people(self):
        pass

    def initiate_conversation(self):
        self.confluence_responder.responder_initiate_conversation()

    def new_topic_of_conversation(self):
        self.confluence_responder.responder_new_topic_of_conversation()

    def leave_conversation(self):
        self.confluence_responder.responder_leave_conversation()
