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
from matchmaking_responder import matchmaking_responder

matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}

class matchmaking():
    def __init__(self, responder):
        print('[BOTS/MATCHMAKING] Starting...')

        self.aiml = aiml.Kernel()
        self.aiml.learn("bots/matchmaking/std-startup.xml")
        self.aiml.respond("load aiml b")

        self.matchmaking_responder = matchmaking_responder(responder)

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

        self.aiml.respond(self.utterance)
        responder = self.aiml.getPredicate('responder')

        print('[BOTS/MATCHMAKING] Routing:', responder)

        if self.handoffStatus == 1:
            self.matchmaking_like_process_2()
            return -1
        else:
            if driver == 1:
                self.drivers()
                return self.lockcode
            else:
                if responder == "matchmaking_like":
                    print("[BOTS/MATCHMAKING] matchmaking_like")
                    self.matchmaking_like()
                    return self.lockcode

                elif responder == "matchmaking_dislike":
                    print("[BOTS/MATCHMAKING] matchmaking_dislike")
                    self.matchmaking_dislike()
                    return self.lockcode

                elif responder == "matchmaking_forget_like":
                    print("[BOTS/MATCHMAKING] matchmaking_forget_like")
                    self.matchmaking_forget_like()
                    return self.lockcode

                elif responder == "matchmaking_forget_dislike":
                    print("[BOTS/MATCHMAKING] matchmaking_forget_dislike")
                    self.matchmaking_forget_dislike()
                    return self.lockcode

                elif responder == "matchmaking_matchmake":
                    print("[BOTS/MATCHMAKING] matchmaking_matchmake")
                    self.matchmaking_matchmake()
                    return self.lockcode

                elif responder == "matchmaking_enquire":
                    print("[BOTS/MATCHMAKING] matchmaking_enquire")
                    self.matchmaking_enquire()
                    return self.lockcode
                
                else:
                    response = "Sorry, I didn't quite get that. Please try a different phrase."
                    self.responder.respond(response)
                    self.drivers()
                    return self.lockcode

    def matchmaking_like(self):
        self.aiml.respond(self.utterance)
        predicate = self.aiml.getPredicate('like')

        url = "http://localhost:3000/api/person/add/likeDislike"

        payload = "likeDislike=true&thing=" + predicate + "&forename=" + self.forename_1.title()
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "c4a150d4-eb1a-431d-b68a-1fc99aecf28d"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        # Check if this is a common like, discusses if true
        commonLikeAvailable, text = self.quickCheck(predicate)

        test = random.uniform(0, 1)

        if commonLikeAvailable:
            if test > 0.5:
                # Check is user wants to know more
                self.matchmaking_like_process_1(predicate)
            else:
                response = text
                self.responder.respond(response)
        else:
            self.matchmaking_responder.responder_like(predicate)

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

        self.matchmaking_responder.responder_dislike(predicate)
        self.drivers()

    def matchmaking_forget_like(self):
        self.matchmaking_responder.responder_forget_like()

    def matchmaking_forget_dislike(self):
        self.matchmaking_responder.responder_forget_dislike()

    def matchmaking_matchmake(self):
        self.aiml.respond(self.utterance)
        friend = self.aiml.getPredicate('friend')
        thing = self.aiml.getPredicate('thing')
        matchmake = self.aiml.getPredicate('matchmake')

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
                self.matchmaking_responder.responder_matchmake_not_found()
            else:
                rand = random.randint(0, len(friends)-1)
                self.matchmaking_responder.responder_matchmake_found(friends[rand], things[rand])
                self.driversMatchmaking()

        elif matchmake == "SPECIFIC FRIEND":
            self.forename_2 = friend.title()
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

            if len(likes["commonLikes"]) > 1:
                rand = random.randint(0, len(likes["commonLikes"])-1)
                self.matchmaking_responder.responder_matchmake_found_specific_friend(likes["commonLikes"][rand])
            else:
                response = "Sorry, you do not have anything in common with " + self.forename_2
                self.responder.respond(response)
            
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
                    if(like["thing"].lower() == self.thing.lower() and person["forename"] != self.forename_1):
                        friends.append(person["forename"])
                        things.append(like["thing"])

            if len(friends) >= 1:
                rand = random.randint(0, len(friends)-1)
                self.matchmaking_responder.responder_matchmake_found(friends[rand], things[rand])
            else:
                response = "Sorry, no one else you know likes " + thing
                self.responder.respond(response)

        else:
            print('[BOTS/MATCHMAKING] Invalid responder value. Check bots/matchmaking/aiml/*.aiml')

    def matchmaking_enquire(self):
        self.aiml.respond(self.utterance)
        friend = self.aiml.getPredicate('friend')

        url = "http://localhost:3000/api/person/likes"

        payload = "forename=" + friend.title()
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "c29574dd-a784-474d-8c8f-ba83177e0448"
            }

        likes = requests.request("POST", url, data=payload, headers=headers)
        likes = json.loads(str(likes.text))

        count = 0

        rand = random.randint(0, len(likes["likes"])-1)
        self.matchmaking_responder.responder_matchmake_enquire(friend, likes["likes"][rand]["thing"])

    def drivers(self):
        self.matchmaking_responder.responder_drivers()

    def driversMatchmaking(self):
        self.matchmaking_responder.responder_driversMatchmaking()

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

        resp = 'null'
        canRespond = False

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
            canRespond = True
        
        return canRespond, resp

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
            self.matchmaking_like_process_3()
        elif predicate == "NO":
            self.handoffStatus = 0
            self.drivers()
        else:
            self.matchmaking_like_process_1(self.handoffLike)
            print('invalid case')

    def matchmaking_like_process_3(self):
        self.handoffStatus = 0
        self.responder.handoff(self.handoffLike)

        print('Handoff to Alana would happen here.')

    def promptLikes(self):
        self.matchmaking_responder.responder_promptLikes()