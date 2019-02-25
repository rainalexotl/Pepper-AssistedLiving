import json#needed for json manipulation (state is json data)

import requests#used for testing


#this is for TEST PURPOSES ONLY. This program will (hopefully) allow for unit testing of the bots, simulating the Alana system as a whole.


CarryOn = True

Conversation = ""#the conversational string

name = ''

Attributes = {}

Last_bot = ''#needed so that the program will know which bot was spoken to last

Conversation = input("please start by entering the name of the question file: ")

while CarryOn == True:

    try:#ensures graceful failure in the event of an exception

        r = requests.post('http://0.0.0.0:5111/', json={'current_state': {'bot_states' : {name : Attributes},'state' : {'last_bot' : Last_bot, 'input' : {'text' : Conversation}}}})

        r.json()#if the response is not proper json, it should crash here

        data = json.loads(r.text)[0]

        print("The bot called " + data["bot_name"] + " responded with '" + data["result"].rstrip() + "'.")#the rstrip() is needed to remove newlines

        Attributes = data['user_attributes']

        name = data["bot_name"]

        Last_bot = name#this is the last bot that was selected to speak to the user.

        Conversation = input("please enter your message here: ")

    except :

        print("Ending Program.")

        CarryOn = False
