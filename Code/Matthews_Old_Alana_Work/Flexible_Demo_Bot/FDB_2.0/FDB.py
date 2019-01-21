# from utils.dict_query import DictQuery  # For use with Python 2.7
import logging#logging allows for a record of runtime events (useful for debugging) I likely won't use it much
import os#this allows for OS-independant funtionality, I may use it for file-handling

from flask import Flask, request#flask stuff, used for web-based functions. I shouldn't change or interact much with this
from flask_restful import Api#flask stuff, used for web-based functions. I shouldn't change or interact much with this
from utils.abstract_classes import Bot#the class which I'm extending here. Many bots run in parallel, and they are selected between.

import re#needed for regular expressions, which aid in input validation
import sys#used to get initial file


app = Flask(__name__)
api = Api(app)
BOT_NAME = 'Flexible_Demo_Bot'

logger = logging.getLogger(__name__)

class FDB(Bot):

    def __init__(self):
        super(FDB, self).__init__(bot_name=BOT_NAME)

        self.statements = []#the store of statements, including their expected answer (if applicable). This should be accessible anywhere in the FDB object

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        if len(sys.argv) > 1:

            print("started reading from file: " + sys.argv[1])

            try:

                File = open(sys.argv[1], "r")

                Question = ""#the question

                Answer = ""#the expected answer

                for line in File:

                    #parse file content

                    if line[:8] == "Program:":
                        #case for question
                        Question = line[8:].rstrip().lstrip()
                    elif line[:5] == "User:":
                        #case for expected answers (later versions of this program will compare answers to questions)
                        Answer = line[5:].rstrip().lstrip()
                        self.statements.append((Question, Answer))#adds the question answer pair as a tuple (this assumes that in the input file, every question will have an answer even if it's blank)
                    else:
                        print("File contents improper.")
                        sys.exit()

                    #finish parsing

                File.close()

                print("finished reading from file: " + sys.argv[1])

            except:

                print("Error when reading from file.")
                sys.exit()

        else:
            print("No filename!")
            sys.exit()

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

    def get(self):
        return "Flexible Demo Bot Version 2.0"#used so that if someone tries a get method on this bot (using a browser, for example) they see this message

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

    def post(self):

        request_data = request.get_json(force=True)

        Input = request_data['current_state']['state']['input']['text']

        print("User said '" + Input + "'.")

        Attributes = {}

        Attributes['QNum'] = 0#start at zero

        start = False#determines if the program is just starting (if this is the case, what the user says doesn't matter)

        Valid = True#stores whether or not the users response was appropriate to the script

        self.response.lock_requested = False#by default, the program should not request a lock

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        if BOT_NAME in request_data['current_state']['bot_states']:#this checks if the user has spoken to this bot before
            Attributes = request_data['current_state']['bot_states'][BOT_NAME]#retrieves this bot's attribute list (if it exists)
            print("This program has been posted to before.")
        else:
            print("This program has never been posted to before.")
            start = True

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        #here, the program works out whether to ask the user a question

        if Attributes['QNum'] < len(self.statements):#in this scenario, it's time to ask a question

            self.response.result = self.statements[Attributes['QNum']][0]#access the first part of the question/asnwer tuple

        else:# in this scenario all the questions have been both asked and answered

            self.response.result = "That's it, we're done."

            Valid = False#no reason to request a lock, this bot is finished with the user

        #response to user ends here

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        #here, the program evaluates the user input

        if Valid:#(later versions will use more sophisticated techniques such as cosine simularity, this is just accepts anything)
            self.response.lock_requested = True#request a lock if the user responded with a valid response.
            Attributes['QNum'] = Attributes['QNum'] + 1#move to next question

        #input evaluation ends

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        self.response.user_attributes = Attributes#ensures continuity

        return [self.response.toJSON()]

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

api.add_resource(FDB, "/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5111)
    
