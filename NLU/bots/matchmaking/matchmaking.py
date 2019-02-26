from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources

matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}

class matchmaking():
    def __init__(self):
        print('[BOTS/MATCHMAKING] Starting...')
        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/matchmaking/std-startup.xml")
        self.aiml.respond("load aiml b")
        
        self.test = -1

    def check(self, intent):
        print('[BOTS/MATCHMAKING] Responding...')

        if intent == "matchmaking_like":
            print("[BOTS/MATCHMAKING] matchmaking_like")
            self.matchmaking_like()
        elif intent == "matchmaking_dislike":
            print("[BOTS/MATCHMAKING] matchmaking_dislike")
            self.matchmaking_dislike()
        elif intent == "matchmaking_forget_like":
            print("[BOTS/MATCHMAKING] matchmaking_forget_like")
            self.matchmaking_forget_like()
        elif intent == "matchmaking_forget_dislike":
            print("[BOTS/MATCHMAKING] matchmaking_forget_dislike")
            self.matchmaking_forget_dislike()
        elif intent == "matchmaking_matchmake":
            print("[BOTS/MATCHMAKING] matchmaking_matchmake")
            self.matchmaking_matchmake()

        #print(self.test)

    def matchmaking_like(self):
        self.test = 0

        self.aiml.respond("I love oranges")
        predicate = self.aiml.getPredicate('like')

        print(predicate)

    def matchmaking_dislike(self):
        self.test = 1

    def matchmaking_forget_like(self):
        self.test = 2

    def matchmaking_forget_dislike(self):
        self.test = 3

    def matchmaking_matchmake(self):
        self.test = 4