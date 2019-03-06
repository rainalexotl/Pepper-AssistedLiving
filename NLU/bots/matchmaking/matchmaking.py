from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources
import random
import requests

matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}

class matchmaking():
    def __init__(self):
        print('[BOTS/MATCHMAKING] Starting...')

        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/matchmaking/std-startup.xml")
        self.aiml.respond("load aiml b")

        self.utterance = ''
        self.mode = 0

        self.forename = 'Frasier'
        self.forename_1 = self.forename
        self.forename_2 = 'unknown'

        self.lockcode = 1

    def check(self, intent, utterance, forename, driver):
        print('[BOTS/MATCHMAKING] Responding...')

        self.forename = forename
        self.utterance = utterance

        if driver == 1:
            self.drivers()
            return -1
        else:
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
        self.aiml.respond(self.utterance)
        predicate = self.aiml.getPredicate('like')

        url = "http://localhost:3000/api/person/add/likeDislike"

        payload = "likeDislike=true&thing=" + predicate + "&forename=" + self.forename
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
        self.aiml.respond(self.utterance)
        predicate = self.aiml.getPredicate('dislike')

        url = "http://localhost:3000/api/person/add/likeDislike"

        payload = "likeDislike=false&thing=" + predicate + "&forename=" + self.forename
        print(payload)
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "c4a150d4-eb1a-431d-b68a-1fc99aecf28d"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        print(response.text)

        print(predicate)

    def matchmaking_forget_like(self):
        self.test = 2

    def matchmaking_forget_dislike(self):
        self.test = 3

    def matchmaking_matchmake(self):
        self.aiml.respond(self.utterance)
        friend = self.aiml.getPredicate('friend')
        thing = self.aiml.getPredicate('thing')
        matchmake = self.aiml.getPredicate('matchmake')

        if matchmake == "GENERAL":
            url = "http://localhost:3000/api/person/commonlikes"

            payload = "forename_1=" + self.forename_1 + "&forename_2=" + self.forename_2 + "&type=general"
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
                'Postman-Token': "5777f647-b96b-4f17-8d71-906e1e3ae6b2"
            }

            people = requests.request("POST", url, data=payload, headers=headers)
            people = json.loads(str(people.text))

            myLikes = []
            friends = []
            things = []

            for person in people["allPeople"]:
                for like in person["likesDislikes"]:
                    if(person["forename"] == self.forename):
                        myLikes.append(like["thing"])

            for person in people["allPeople"]:
                for like in person["likesDislikes"]:
                    if(like["thing"] in myLikes and person["forename"] != self.forename):
                        friends.append(person["forename"])
                        things.append(like["thing"])

            rand = random.randint(0, len(friends))

            print('It looks like you and', friends[rand], 'both like', things[rand])

        elif matchmake == "SPECIFIC FRIEND":
            self.forename_2 = friend.title()

            url = "http://localhost:3000/api/person/commonlikes"

            payload = "forename_1=" + self.forename_1 + "&forename_2=" + self.forename_2 + "&type=specific_friend"
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
                'Postman-Token': "5777f647-b96b-4f17-8d71-906e1e3ae6b2"
            }

            likes = requests.request("POST", url, data=payload, headers=headers)
            likes = json.loads(str(likes.text))

            rand = random.randint(0, len(likes["commonLikes"]))

            print('It looks like you and', self.forename_2, 'both like', likes["commonLikes"][rand])
            
        elif matchmake == "SPECIFIC THING":
            self.thing = thing

            url = "http://localhost:3000/api/person/commonlikes"

            payload = "forename_1=" + self.forename_1 + "&forename_2=" + self.forename_2 + "&type=general"
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
                'Postman-Token': "5777f647-b96b-4f17-8d71-906e1e3ae6b2"
                }

            people = requests.request("POST", url, data=payload, headers=headers)
            people = json.loads(str(people.text))

            friends = []
            things = []

            for person in people["allPeople"]:
                for like in person["likesDislikes"]:
                    if(like["thing"] == self.thing.lower() and person["forename"] != self.forename):
                        friends.append(person["forename"])
                        things.append(like["thing"])

            rand = random.randint(0, len(friends))

            print('It looks like', friends[rand], 'also likes', things[rand])

        else:
            print('[BOTS/MATCHMAKING] Invalid responder value. Check bots/matchmaking/aiml/*.aiml')

    def drivers(self):
        individual_drivers = []
        individual_drivers.append("Why don't you tell me about some things you like?")
        individual_drivers.append("Can you tell me a bit about what you like?")
        individual_drivers.append("I need to get to know you a bit better. Tell me about something you like or dislike.")
        individual_drivers.append("If you tell me a bit about what you like, I can match you up with other people who like the same things.")

        rand = random.randint(0, len(individual_drivers))
        print(rand)
        print(individual_drivers[rand])