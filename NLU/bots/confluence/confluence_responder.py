import numpy as np
from responder import responder

class confluence_responder():
    def __init__(self, responder):
        self.responder = responder

    def updateNames(self):
        self.forename_1, self.forename_2 = self.responder.getNames()

    # confluence - initiate_introduction
    def responder_initiate_introduction(self):
        self.updateNames()
        choices = []
        choices.append("Hi " + self.forename_1 + " and " + self.forename_2 + ". Would like me to find some things for you to talk about?")
        choices.append("Hello " + self.forename_1 + " and " + self.forename_2 + ". Shall I suggest some things for you to talk about?")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    # confluence - initiate_conversation
    def responder_initiate_conversation(self, commonLike):
        self.updateNames()
        choices = []
        choices.append("From my understanding " + self.forename_1 + ", " + self.forename_2 + " also likes " + commonLike + ". Woud you like to talk about " + commonLike + "?")
        choices.append(self.forename_1 + ", I believe " + self.forename_2 + " also likes " + commonLike+ ". Woud you like to talk about " + commonLike + "?")
        choices.append(self.forename_1 + ", I think " + self.forename_2 + " also likes " + commonLike+ ". Woud you like to talk about " + commonLike + "?")
        choices.append(self.forename_1 + " don't you also like " + commonLike + ", just as " + self.forename_2 + " does? Woud you like to talk about " + commonLike + "?")
        choices.append("What about " + commonLike + "? It seems like a popular interest, I believe you two like it, don't you? Woud you like to talk about " + commonLike + "?")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    # confluence - new_topic_of_conversation
    def responder_new_topic_of_conversation(self):
        self.updateNames()
        choices = []
        choices.append("I know" + self.forename_2 + "also enjoys" + self.common_interest2 + "like you" + self.forename_1)
        choices.append("I believe" + self.forename_2 + "also enjoys" + self.common_interest2 + "like you" + self.forename_1)
        choices.append("I think" + self.forename_2 + "also enjoys" + self.common_interest2 + "like you" + self.forename_1)
        choices.append(self.forename_2 + "don't you also like" + self.common_interest2 + "like" + self.forename_2 + "?")
        choices.append("What about" + self.common_interest2 + "? it seems like a popular interest, I believe you two like it, don't you? ")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    # confluence - leave_conversation
    def responder_leave_conversation(self):
        self.updateNames()
        choices = []
        choices.append("I'm leaving for now " + self.forename_1 + self.forename_2 + " bye for now")
        choices.append("I have to leave " + self.forename_1 + self.forename_2 + " bye for now")
        choices.append("I'm leaving for now " + self.forename_1 + self.forename_2 + " see you later! ")
        choices.append("I have to leave " + self.forename_1 + self.forename_2 + " see you later! ")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_like(self, thing):
        self.updateNames()
        choices = []
        choices.append("Ok, I will remember that you like this.")
        choices.append("Ok, I will remember that.")
        choices.append("Tell me why you like " + thing)
        choices.append("Ok, it is noted.")
        choices.append("Why do you like " + thing + "?")
        choices.append("What do you find good about " + thing + "?")
        choices.append("Great ! I like it too.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    def responder_gather_likes(self, name):
        self.updateNames()
        choices = []
        choices.append(name + ", I don't have enough information about what you like. Please tell me something you like.")
        choices.append("Sorry, " + name + " I don't know much about things you like. Please tell me one now.")
        choices.append("I don't know much of yours likes, " + name + ". Please tell me something you like just now.")
        choice = np.random.choice(choices)
        self.responder.respond(choice)