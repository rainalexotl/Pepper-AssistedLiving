# from utils.dict_query import DictQuery  # For use with Python 2.7
import logging#logging allows for a record of runtime events (useful for debugging) I likely won't use it much
import os#this allows for OS-independant funtionality, I may use it for file-handling

from flask import Flask, request#flask stuff, used for web-based functions. I shouldn't change or interact much with this
from flask_restful import Api#flask stuff, used for web-based functions. I shouldn't change or interact much with this
from utils.abstract_classes import Bot#the class which I'm extending here. Many bots run in parallel, and they are selected between.


app = Flask(__name__)
api = Api(app)
BOT_NAME = 'Flexible_Script_Bot'

logger = logging.getLogger(__name__)

class FSB(Bot):
    def __init__(self):
        super(FSB, self).__init__(bot_name=BOT_NAME)

    def get(self):
        return "Flexible Script Bot Version 1.0"#used so that if someone tries a get method on this bot (using a browser, for example) they see this message

        pass

    def post(self):

        request_data = request.get_json(force=True)
        Input = request_data['state']['input']['text']

        print("post request said " + Input)

        return [self.response.toJSON()]


api.add_resource(FSB, "/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5111)
    
