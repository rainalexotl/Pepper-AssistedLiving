import numpy as np

class initiator_responder():
    def __init__(self, responder):
        self.responder = responder
        self.forename_1, self.forename_2 = self.responder.getNames()

    def updateNames(self):
        self.forename_1, self.forename_2 = self.responder.getNames()

    # initiator - request_forename_1
    def responder_request_forename_1(self):
        self.updateNames()
        choices = []
        choices.append("Hi there, who am I talking with?")
        choices.append("Hello, who am I talking with?")
        choices.append("Hi, what's your name?")
        choices.append("Hello, what's your name?")
        choices.append("Hi, can you tell me your name?")
        choices.append("Hello, can you tell me your name?")
        choices.append("Hi, nice to meet you! What is your name?")
        choices.append("Hello, nice to meet you! What is your name?")
        choices.append("Hi, nice to meet you! How do I call you? ")
        choices.append("Hello, nice to meet you! How do I call you?")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    # initiator - get_forename_1
    def responder_get_forename_1(self):
        self.updateNames()
        choices = []
        choices.append("Ok, " + self.forename_1 + " is there anyone else there with you?")
        choices.append(self.forename_1 + " is there anyone else there with you?")
        choices.append(self.forename_1 + " is anyone else there with you?")
        choices.append(self.forename_1 + " is anyone else accompanying you?")
        choices.append(self.forename_1 + " can you tell me if someone else is there with you ?")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    # initiator - enter_individual_mode
    def responder_enter_individual_mode(self):
        self.updateNames()
        choices = []
        choices.append("No? Ok, let's see what the two of us can talk about.")
        choices.append("Do you want to talk about music?")
        choices.append("Do you want to talk about movies?")
        choices.append("It's down to the both of us! DO you want to talk about music? ")
        choices.append("It's down to the both of us! DO you want to talk about movies? ")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    # initiator - request_forename_2
    def responder_request_forename_2(self):
        self.updateNames()
        choices = []
        choices.append("Ok. Who is it that is with you?")
        choices.append("Ok. Who is with you?")
        choices.append("Ok. What is the name of the person accompanying you? ")
        choices.append("Ok. Who is accompanying you? ")
        choices.append("Who is it that is with you?")
        choices.append("Who is with you?")
        choices.append("What is the name of the person accompanying you? ")
        choices.append("Who is accompanying you? ")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    # initiator - get_forename_2
    def responder_get_forename_2(self):
        self.updateNames()
        choices = []
        choices.append("Ok, I will be glad to talk to you and " + self.forename_2)
        choices.append("Great! I am happy to talk to you and " + self.forename_2)
        choices.append("I will gladly talk to you and " + self.forename_2)
        choices.append("Ok, I will gladly talk to you and " + self.forename_2)
        choices.append("Great ! I will gladly talk to you and " + self.forename_2)
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_get_forename_1_and_forename_2(self):
        self.updateNames()
        choices = []
        choices.append("Ok, " + self.forename_1 + " and " + self.forename_2 + " I will be glad to talk to both of you.")
        choices.append("Hello " + self.forename_1 + " and " + self.forename_2 + " I am glad to speak with you.")
        choices.append("Ok, " + self.forename_1 + " and " + self.forename_2 + " I will be glad to speak with you.")
        choices.append("Hello " + self.forename_1 + " and " + self.forename_2 + " I am glad to talk to you")
        choices.append("Ok, " + self.forename_1 + " and " + self.forename_2 + " I will be glad to speak with both of you.")
        choices.append("Hello " + self.forename_1 + " and " + self.forename_2 + " I am glad to talk to both of you")
        choices.append(self.forename_1 + " and " + self.forename_2 + " It is nice to speak with you.")
        choices.append(self.forename_1 + " and " + self.forename_2 + " It is nice to talk to you.")
        choices.append("Hello " + self.forename_1 + " and " + self.forename_2 + " It is nice to speak with you.")
        choices.append("Hello " + self.forename_1 + " and " + self.forename_2 + " It is nice to talk to you.")
        choices.append("Hi " + self.forename_1 + " and " + self.forename_2 + " It is nice to speak with you.")
        choices.append("Hi " + self.forename_1 + " and " + self.forename_2 + " It is nice to talk to you.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)