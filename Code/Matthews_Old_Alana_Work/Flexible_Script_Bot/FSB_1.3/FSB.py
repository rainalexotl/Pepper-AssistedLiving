# from utils.dict_query import DictQuery  # For use with Python 2.7
import logging#logging allows for a record of runtime events (useful for debugging) I likely won't use it much
import os#this allows for OS-independant funtionality, I may use it for file-handling

from flask import Flask, request#flask stuff, used for web-based functions. I shouldn't change or interact much with this
from flask_restful import Api#flask stuff, used for web-based functions. I shouldn't change or interact much with this
from utils.abstract_classes import Bot#the class which I'm extending here. Many bots run in parallel, and they are selected between.

import re#needed for regular expressions, which allow for input validation

app = Flask(__name__)
api = Api(app)
BOT_NAME = 'Flexible_Script_Bot'

logger = logging.getLogger(__name__)

class FSB(Bot):
    def __init__(self):
        super(FSB, self).__init__(bot_name=BOT_NAME)

    def get(self):
        return "Flexible Script Bot Version 1.3"#used so that if someone tries a get method on this bot (using a browser, for example) they see this message

    def validate(self, answer, Type):
        if (Type == "numerical"):#this should return true if the value is an integer (positive or negative), but otherwise return false.
            if re.match('[+-]?(\d)+[.]?(\d)+',answer):#this should only be true if the input is a valid integer or float
                return True
            else:
                return False
        if (Type == "text"):
            return True
        if (Type == "yesno"):#this should only return true of the answer can be parsed doown to a yes or a no. this won't be easy, and will require a lot of revision
            if re.search('(,| |^)([Yy]es|[Nn]o)?(,|$| |\.)',answer):#this should only happen if the sentence contains 'yes' and or 'no' as complete words, not parts of other words.
                return True
            else:
                return False
        else:#this shouldn't ever happen, but a malformed or invalid file might trigger it. For now, it will return True, but there should be a special action here
            print("invalid type error, " + Type + " is not a proper type!")
            return True

    def post(self):

        request_data = request.get_json(force=True)

        Input = request_data['current_state']['state']['input']['text']

        print("User said '" + Input + "'.")

        Attributes = {}

        Attributes['Answers'] = []#this will hold all the answers

        Attributes['QNum'] = 0

        Attributes['FileName'] = ""

        Questions = []#this will hold all the questions

        QTypes = []#this will hold all the question TYPES

        #preliminary operations/declarations end

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        if BOT_NAME in request_data['current_state']['bot_states']:
            Attributes = request_data['current_state']['bot_states'][BOT_NAME]#retrieves this bot's attribute list (if it exists)
            if Attributes['QNum'] > 0:
                print("Currently on Question Number: " + str(Attributes['QNum']) + ".")
            else:
                print("Questioning has not yet begun, due to a valid file not yet being recieved.")
                Attributes['FileName'] = Input
        else:
            print("We are at the beginning.")
            Attributes['FileName'] = Input

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        #now, it's time to read from the file, if an appropriate name is found

        try:

            File = open(Attributes['FileName'], "r")

            for line in File:

                Questions.append(line.split(",")[0].rstrip())#adds the question

                QTypes.append(line.split(",")[1].rstrip())#adds the question type

            File.close()

            Attributes['QNum'] = Attributes['QNum'] + 1

        except:
            pass#a placeholder

        #file reading ends here

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        #here, the answers to questions are stored 9assuming valid type)

        correctType = True#this will store the answer to whether or not the question type matches the answer type

        if Attributes['QNum'] > 1:#in this scenario, the user has already answered the previous question, and the current input is the answer to the previous question

            if self.validate(Input,QTypes[Attributes['QNum'] - 2]):#checks the type of the question

                Attributes['Answers'].append(Input)#adds the necessary answer

            else:

                Attributes['QNum'] = Attributes['QNum'] - 1#decrement question number, the question must be asked again

                correctType = False#this will store the answer to whether or not the question type matches the answer type

        else:#no action should be taken, at least in this version of the program, this means that no answers have been submitted
            pass

        #answer storage ends here

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        #here, the program works out how to respond to the user

        if Attributes['QNum'] > 0 and Attributes['QNum'] <= len(Questions) and len(Questions) > 0:#in this scenario, it's time to answer questions

            if correctType:
                self.response.result = Questions[Attributes['QNum'] - 1]#respond with the question the bot must ask of the user
            else:
                self.response.result = ("The answer you gave was of an invalid type. Please try another answer to the question: " + Questions[Attributes['QNum'] - 1])#prompt user to try again

        elif Attributes['QNum'] > len(Questions):#if this happens then it means (theoretically) that every question has been answered

            self.response.result = "That's it, you have answered all questions!"

            #▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

            #here is where the answers will be printed to file, eventually, once that feature is implemented

            File = open(("Answers_" + Attributes['FileName']), "w")

            for answer in Attributes['Answers']:

                File.write(answer)

                File.write("\n")

            File.close()

            Attributes['QNum'] = Attributes['QNum'] + 1            

            #file printing ends here

            #▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        else:#if this happens, no valid filename was given OR the given file was empty

            self.response.result = "Invalid file, please provide a better one."#ask for a better filename

            Attributes['QNum'] = 0#this should be zero


        #response to user ends here

#▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣

        self.response.user_attributes = Attributes#ensures continuity

        return [self.response.toJSON()]


api.add_resource(FSB, "/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5111)
    
