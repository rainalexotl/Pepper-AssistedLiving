import numpy as np
from responder import responder


class confluence_responder():
    def __init__(self):
        self.responder = responder()

    def updateNames(self):
        self.forename_1, self.forename_2 = self.responder.getNames()

    # confluence - initiate_introduction
    def responder_initiate_introduction(self):
        self.updateNames()
        choices = []
        choices.append("Hi" + self.forename_1 + "and" + self.forename_2)
        choices.append("Hello" + self.forename_1 + "and" + self.forename_2)
        choices.append("Hi" + self.forename_1 + "and" + self.forename_2 + "How are you doing?")
        choices.append("Hello" + self.forename_1 + "and" + self.forename_2 + "How are you doing?")
        choices.append("Hi" + self.forename_1 + "and" + self.forename_2 + "How are you?")
        choices.append("Hello" + self.forename_1 + "and" + self.forename_2 + "How are you?")
        choice = np.random.choice(choices)
        self.responder.respond(choice)

    # confluence - initiate_conversation
    def responder_initiate_conversation(self):
        self.updateNames()
        choices = []
        choices.append("From my understanding" + self.forename_1 + self.forename_2 + "also likes" + self.common_interest1)
        choices.append(self.forename_1 + "I believe" + self.forename_2 + "also likes" + self.common_interest1)
        choices.append(self.forename_1 + "I think" + self.forename_2 + "also likes" + self.common_interest1)
        choices.append(self.forename_1 + "don't you also like" + self.common_interest1 + "like" + self.forename_2 + "?")
        choices.append("What about" + self.common_interest1 + "? it seems like a popular interest, I believe you two like it, don't you? ")
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