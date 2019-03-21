import numpy as np
import time

class matchmaking_responder():
    def __init__(self, responder):
        self.responder = responder
        self.forename_1, self.forename_2 = self.responder.getNames()

        np.random.seed()
        
    def updateNames(self):
        self.forename_1, self.forename_2 = self.responder.getNames()

    # matchmaking - initiate_introduction
    def responder_like(self, thing):
        self.updateNames()
        choices = []
        choices.append("Ok, I will remember that you like this.")
        choices.append("Ok, I will remember that.")
        # choices.append("Tell me why you like " + thing)
        choices.append("Ok, it is noted.")
        # choices.append("Why do you like " + thing + "?")
        # choices.append("What do you find good about " + thing + "?")
        choices.append("Great ! I like it too.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_dislike(self, thing):
        self.updateNames()
        choices = []
        choices.append("Ok, I will remember that you dislike this.")
        choices.append("Ok, I will remember that.")
        choices.append("Tell me why you dislike " + thing)
        choices.append("Ok, it is noted.")
        choices.append("Why do you dislike " + thing + "?")
        choices.append("What do you find bad about " + thing + "?")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_forget_like(self):
        self.updateNames()
        choices = []
        choices.append("Sorry, I am not able to modify your likes and dislikes yet.")
        choices.append("Sorry, I can't modify your likes and dislikes yet.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_forget_dislike(self):
        self.updateNames()
        choices = []
        choices.append("Sorry, I am not able to modify your likes and dislikes yet.")
        choices.append("Sorry, I can't modify your likes and dislikes yet.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_matchmake_not_found(self):
        self.updateNames()
        choices = []
        choices.append("Sorry, I can't find any common interests for you just now. Try telling me more about what you like.")
        choices.append("Sorry, I can't find any common interests for you just now. Tell me more about what you like.")
        choices.append("Sorry, I can't find any common interests for you just now. What do you like?")
        choices.append("Sorry, I can't find any common interests for you just now. What do you like to do ?")
        choices.append("Sorry, I did't find any common interests. What do you like to do ?")
        choices.append("Sorry, I did't find any common interests. Try telling me more about what you like.")
        choices.append("Sorry, I did't find any common interests. Tell me more about what you like.")
        choices.append("Sorry, I did't find any common interests. What do you like?")
        choices.append("Try telling me more about what you like. I could not find any common interests.")
        choices.append("Tell me more about what you like. I could not find any common interests.")
        choices.append("What do you like? I could not find any common interests.")
        choices.append("What do you like to do ? I could not find any common interests.")
        choices.append("What do you like to do ? I could not find any common interests.")
        choices.append("Try telling me more about what you like. I could not find any common interests.")
        choices.append("Tell me more about what you like. I could not find any common interests.")
        choices.append("What do you like? I could not find any common interests.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_matchmake_found(self, friends, things):
        self.updateNames()
        choices = []
        choices.append("It looks like you and " + friends + " both like " + things + ".")
        choices.append("Did you know that you and " + friends + " both like " + things + "?")
        choices.append("It appears to me that you and " + friends + " both like " + things + ".")
        choices.append("It looks like " + friends + " also likes " + things + ".")
        choices.append("Did you know that " + friends + " also likes " + things + "?")
        choices.append("It appears to me that " + friends + " also likes " + things + ".")
        choices.append("Do you know " + friends + "? " + friends + " also likes " + things + "?")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_matchmake_enquire(self, friend, thing):
        self.updateNames()
        choices = []
        choices.append(friend + " likes " + thing)
        choices.append(friend + " is font of " + thing)
        choices.append("Your friend " + friend + " likes  " + thing)
        choices.append("I can see that " + friend + " likes " + thing)
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_matchmake_found_specific_friend(self, things):
        self.updateNames()
        choices = []
        choices.append("It looks like you and " + self.forename_2 + " both like " + things)
        choices.append("Did you know that you and " + self.forename_2 + " both like " + things)
        choices.append("It appears to me that you and " + self.forename_2 + " both like " + things)
        choices.append("It looks like " + self.forename_2 + " also likes " + things)
        choices.append("Did you know that " + self.forename_2 + " also likes " + things)
        choices.append("It appears to me that " + self.forename_2 + " also likes " + things)
        choices.append("Do you know " + self.forename_2 + "? " + self.forename_2 + " also likes " + things)
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_drivers(self):
        self.updateNames()
        choices = []
        choices.append("Why don't you tell me about some of the things you like?")
        choices.append("Why don't you tell me about some of the things you do not like?")
        choices.append("Can you tell me a bit more about what you like?")
        choices.append("I need to get to know you a bit better. Tell me about something you like or dislike.")
        choices.append("If you tell me a bit about what you like, I can match you up with other people who like the same things.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_driversMatchmaking(self):
        self.updateNames()
        choices = []
        choices.append("You know, I can tell you what you have in common with a specific friend, if you ask.")
        choices.append("I would be happy to tell you which of your friends also likes a certain thing that you like, if you ask.")
        choices.append("Why not try asking me about what you and a certain friend both like?")
        choices.append("You can ask me to tell you what you have in common with one of your friends.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_promptLikes(self):
        self.updateNames()
        choices = []
        choices.append("Sorry, I don't have enough information about what you like to answer that. Please tell me some things you like.")
        choices.append("Hmm... I need you to tell me a bit more about what you like first.")
        choices.append("Sorry, I don't know anything about what you like.")
        choices.append("Sorry, you will have to tell me what you like first. I don't know anything about it yet.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)