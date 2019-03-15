from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources
import random
import requests
import sys

sys.path.append("...")
from responder import responder

matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}

class matchmaking():
    def __init__(self, responder):
        print('[BOTS/MATCHMAKING] Starting...')

        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/matchmaking/std-startup.xml")
        self.aiml.respond("load aiml b")

        self.aiml_affirm = aiml.Kernel()
        self.aiml_affirm.learn("bots/matchmaking/std-startup-affirm.xml")
        self.aiml_affirm.respond("load aiml b")

        self.responder = responder

        self.utterance = ''
        self.mode = 0

        self.handoffLike = ''
        self.handoffStatus = 0

        self.forename_1, self.forename_2 = self.responder.getNames()

        self.lockcode = 1

    def check(self, intent, utterance, forename, driver):
        print('[BOTS/MATCHMAKING] Responding...')

        self.forename_1, self.forename_2 = self.responder.getNames()
        self.utterance = utterance

        if self.handoffStatus == 1:
            self.matchmaking_like_process_2()
            return -1
        else:
            if driver == 1:
                self.drivers()
                return self.lockcode
            else:
                if intent == "matchmaking_like":
                    print("[BOTS/MATCHMAKING] matchmaking_like")
                    self.matchmaking_like()
                    return self.lockcode

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
                
                else:
                    self.drivers()
                    return -1

    def matchmaking_like(self):
        self.aiml.respond(self.utterance)
        predicate = self.aiml.getPredicate('like')

        url = "http://localhost:3000/api/person/add/likeDislike"

        payload = "likeDislike=true&thing=" + predicate + "&forename=" + self.forename_1
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "c4a150d4-eb1a-431d-b68a-1fc99aecf28d"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        resp = 'Ok, I will remember that you like this.'
        self.responder.respond(resp)

        # Check if this is a common like, discusses if true
        self.quickCheck(predicate)

        # Check is user wants to know more
        self.matchmaking_like_process_1(predicate)

        sufficientLikes = self.checkLikes()
        if sufficientLikes == True and self.handoffStatus == 0:
            self.driversMatchmaking()
        elif sufficientLikes == False and self.handoffStatus == 0:
            self.drivers()

    def matchmaking_dislike(self):
        self.aiml.respond(self.utterance)
        predicate = self.aiml.getPredicate('dislike')

        url = "http://localhost:3000/api/person/add/likeDislike"

        payload = "likeDislike=false&thing=" + predicate + "&forename=" + self.forename_1
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "c4a150d4-eb1a-431d-b68a-1fc99aecf28d"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        resp = 'Ok, I will remember that you dislike this.'
        self.responder.respond(resp)
        self.drivers()

    def matchmaking_forget_like(self):
        resp = 'Sorry, I am not able to modify your likes and dislikes yet.'
        self.responder.respond(resp)

    def matchmaking_forget_dislike(self):
        resp = 'Sorry, I am not able to modify your likes and dislikes yet.'
        self.responder.respond(resp)

    def matchmaking_matchmake(self):
        self.aiml.respond(self.utterance)
        friend = self.aiml.getPredicate('friend')
        thing = self.aiml.getPredicate('thing')
        matchmake = self.aiml.getPredicate('matchmake')

        print(matchmake)

        sufficientLikes = self.checkLikes()
        if sufficientLikes == False:
            self.promptLikes()
            return

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
                    if(person["forename"] == self.forename_1):
                        myLikes.append(like["thing"])

            for person in people["allPeople"]:
                for like in person["likesDislikes"]:
                    if(like["thing"] in myLikes and person["forename"] != self.forename_1):
                        friends.append(person["forename"])
                        things.append(like["thing"])

            if len(friends) < 2:
                resp = 'Sorry, I cant find any common interests for you just now. Try telling me more about what you like.'
                self.responder.respond(resp)
            else:
                rand = random.randint(0, len(friends)-1)
                resp = 'It looks like you and ' + friends[rand] + ' both like ' + things[rand]
                self.responder.respond(resp)
                self.driversMatchmaking()

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

            rand = random.randint(0, len(likes["commonLikes"])-1)

            resp = 'It looks like you and ' + self.forename_2 + ' both like ' + likes["commonLikes"][rand]
            self.responder.respond(resp)
            
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
                    if(like["thing"] == self.thing.lower() and person["forename"] != self.forename_1):
                        friends.append(person["forename"])
                        things.append(like["thing"])

            rand = random.randint(0, len(friends))

            resp = 'It looks like ' + friends[rand] + ' also likes ' + things[rand]
            self.responder.respond(resp)

        else:
            print('[BOTS/MATCHMAKING] Invalid responder value. Check bots/matchmaking/aiml/*.aiml')

    def drivers(self):
        individual_drivers = []
        individual_drivers.append("Why don't you tell me about some of the things you like?")
        individual_drivers.append("Why don't you tell me about some of the things you do not like?")
        individual_drivers.append("Can you tell me a bit more about what you like?")
        individual_drivers.append("I need to get to know you a bit better. Tell me about something you like or dislike.")
        individual_drivers.append("If you tell me a bit about what you like, I can match you up with other people who like the same things.")

        rand = random.randint(0, len(individual_drivers)-1)
        resp = individual_drivers[rand]
        self.responder.respond(resp)

    def driversMatchmaking(self):
        matchmaking_drivers = []
        matchmaking_drivers.append("You know, I can tell you what you have in common with a specific friend, if you ask.")
        matchmaking_drivers.append("I would be happy to tell you which of your friends also likes a certain thing that you like, if you ask.")
        matchmaking_drivers.append("Why not try asking me about what you and a certain friend both like?")

        rand = random.randint(0, len(matchmaking_drivers)-1)
        resp = matchmaking_drivers[rand]
        self.responder.respond(resp)

    def checkLikes(self):
        url = "http://localhost:3000/api/person/likes"

        payload = "forename=" + self.forename_1
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

    def quickCheck(self, like):
        url = "http://localhost:3000/api/person/commonlikes"

        payload = "forename_1=" + self.forename_1 + "&type=general"
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
                if(person["forename"] == self.forename_1):
                    myLikes.append(like["thing"])

        for person in people["allPeople"]:
            for like in person["likesDislikes"]:
                if(like["thing"] in myLikes and person["forename"] != self.forename_1):
                    friends.append(person["forename"])
                    things.append(like["thing"])

        if len(friends) > 2:
            rand = random.randint(0, len(friends)-1)
            resp = 'It looks like you and ' + friends[rand] + ' both like ' + things[rand]
            self.responder.respond(resp)

    def matchmaking_like_process_1(self, like):
        self.handoffLike = like
        self.handoffStatus = 1

        affirmations = []
        affirmation = 'Would you like me to tell you more about ' + like + '?'
        affirmations.append(affirmation)
        affirmation = 'Should I talk some more about ' + like + '?'
        affirmations.append(affirmation)

        rand = random.randint(0, len(affirmations)-1)
        resp = affirmations[rand]
        self.responder.respond(resp)

    def matchmaking_like_process_2(self):
        self.aiml_affirm.respond(self.utterance)
        predicate = self.aiml_affirm.getPredicate('affirm')

        if predicate == "YES":
            print('they want to know more')
            self.matchmaking_like_process_3()
        elif predicate == "NO":
            print('they do not want to be told any more')
            self.handoffStatus = 0
            self.drivers()
        else:
            self.matchmaking_like_process_1(self.handoffLike)
            print('invalid case')



    def matchmaking_like_process_3(self):
        self.handoffStatus = 0
        self.responder.handoff(self.handoffLike)

    def promptLikes(self):
        likes_prompts = []
        likes_prompts.append("Sorry, I don't have enough information about what you like to answer that. Please tell me some things you like.")
        likes_prompts.append("Hmm... I need you to tell me a bit more about what you like first.")

        rand = random.randint(0, len(likes_prompts)-1)
        resp = likes_prompts[rand]
        self.responder.respond(resp)