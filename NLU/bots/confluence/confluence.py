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
        
        self.aiml_mm = aiml.Kernel()
        self.aiml_mm.learn("bots/matchmaking/std-startup.xml")
        self.aiml_mm.respond("load aiml b")

        self.responder = responder
        self.confluence_responder = confluence_responder(responder)

        self.utterance = ''
        self.forename_1, self.forename_2 = self.responder.getNames()

        self.init = 1
        
        self.affirmStatus = 0
        self.affirmCaller = ''
        self.affirm = 0

        self.likeGatherStatus = 0
        self.likeGatherName = ''

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

        if self.likeGatherStatus == 1:
            responder = self.saveLike()

        if self.init == 1:
            ready, responder = self.checkReady()
        if self.init == 0:
            ready, discard = self.checkReady()

        if ready:
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
        print('confluence_initiate_confirm', self.affirm)
        if self.affirm == 1:
            print('confluence_initiate_confirm true')
            self.populateCommonLikes()
            self.confluence_initiate_conversation()
            return self.lockcode
        else:
            print('confluence_initiate_confirm false')
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

        print('Populating self.stackLikes')
        print('# Common Likes:', len(likes["commonLikes"]))

        for i in range(0, len(likes["commonLikes"])):
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

    # Assistive Functions

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

    def checkReady(self):
        ready_1 = self.checkLikes(self.forename_1)
        ready_2 = self.checkLikes(self.forename_2)

        ready = False
        responder = ''

        if ready_1 and ready_2:
            if self.init == 1:
                responder = "confluence_initiate_introduction"
                self.init = 0
            ready = True
        elif not ready_1 and ready_2:
            self.gatherLikes(self.forename_1)
            ready = False
        elif ready_1 and not ready_2:
            self.gatherLikes(self.forename_2)
            ready = False
        else:
            self.gatherLikes(self.forename_1)
            ready = False

        return ready, responder

    def checkLikes(self, name):
        url = "http://localhost:3000/api/person/likes"

        payload = "forename=" + name
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "c29574dd-a784-474d-8c8f-ba83177e0448"
            }

        likes = requests.request("POST", url, data=payload, headers=headers)
        likes = json.loads(str(likes.text))

        count = 0
        for likes in likes["likes"]:
            count = count + 1
        
        if count > 2:
            return True
        else:
            return False

    def gatherLikes(self, name):
        self.confluence_responder.responder_gather_likes(name)

        self.likeGatherStatus = 1
        self.likeGatherName = name
    
    def saveLike(self):
        self.checkPerson(self.likeGatherName)

        self.aiml_mm.respond(self.utterance)
        predicate = self.aiml_mm.getPredicate('like')

        url = "http://localhost:3000/api/person/add/likeDislike"

        payload = "likeDislike=true&thing=" + predicate + "&forename=" + self.likeGatherName.title()
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "c4a150d4-eb1a-431d-b68a-1fc99aecf28d"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        self.likeGatherStatus = 0

        responder = "confluence_initiate_introduction"

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