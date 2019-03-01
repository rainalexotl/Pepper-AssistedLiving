from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources
import requests

matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}

class matchmaking():
    def __init__(self):
        print('[BOTS/MATCHMAKING] Starting...')

        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/matchmaking/std-startup.xml")
        self.aiml.respond("load aiml b")

        self.test = -1

        self.lockcode = 1

    def check(self, intent, utterance):
        print('[BOTS/MATCHMAKING] Responding...')

        if intent == "matchmaking_like":
            print("[BOTS/MATCHMAKING] matchmaking_like")
            self.matchmaking_like()
            return -1

        elif intent == "matchmaking_dislike":
            print("[BOTS/MATCHMAKING] matchmaking_dislike")
            self.matchmaking_dislike()
            return -1

        elif intent == "matchmaking_forget_like":
            print("[BOTS/MATCHMAKING] matchmaking_forget_like")
            self.matchmaking_forget_like()
            return -1

        elif intent == "matchmaking_forget_dislike":
            print("[BOTS/MATCHMAKING] matchmaking_forget_dislike")
            self.matchmaking_forget_dislike()
            return -1

        elif intent == "matchmaking_matchmake":
            print("[BOTS/MATCHMAKING] matchmaking_matchmake")
            self.matchmaking_matchmake()
            return -1

        print(self.test)

    def matchmaking_like(self):
        self.test = 0

        self.aiml.respond("I love coffee")
        predicate = self.aiml.getPredicate('like')

        url = "http://localhost:3000/api/person/add/likeDislike"

        payload = "likeDislike=true&thing=" + predicate + "&forename=Frasier&surname=Crane"
        print(payload)
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "c4a150d4-eb1a-431d-b68a-1fc99aecf28d"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        print(response.text)

        print(predicate)

    def matchmaking_dislike(self):
        self.test = 1

    def matchmaking_forget_like(self):
        self.test = 2

    def matchmaking_forget_dislike(self):
        self.test = 3

    def matchmaking_matchmake(self):
        self.test = 4