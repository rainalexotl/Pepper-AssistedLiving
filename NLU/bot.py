from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer, Metadata, Interpreter
from rasa_nlu import config

from bots.matchmaking import matchmaking

import json

chit_chat_strings   = {"greet", "thank", "affirm", "bye"}
matchmaking_strings = {"matchmaking_like", "matchmaking_dislike", "matchmaking_forget_like",
                        "matchmaking_forget_dislike", "matchmaking_matchmake"}
calendar_strings    = {""}
recall_strings      = {""}

def train (data, config_file, model_dir):
    training_data = load_data(data)
    configuration = config.load(config_file)
    trainer = Trainer(configuration)
    trainer.train(training_data)
    #model_directory = trainer.persist(model_dir, fixed_model_name = 'chat')

def run():
    interpreter = Interpreter.load('./models/default')

    result = interpreter.parse('I love Mark')

    routing(result)

def routing(result):
    intent = result["intent"]
    intent_name = intent["name"]
    intent_conf = intent["confidence"]

    print('')
    print('*** INTENT ***')
    print('Intent: ', intent_name)
    print('Conf.: ', intent_conf)
    print('')

    if intent_name in chit_chat_strings:
        print('Selecting... Bot 0: Chit Chat')
    elif intent_name in matchmaking_strings:
        print('Selecting... Bot 1: Matchmaking')
        matchmaking.run()
    elif intent_name in calendar_strings:
        print('Selecting... Bot 2: Calendar')
    elif intent_name in recall_strings:
        print('Selecting... Bot 3: Recall Quiz')

    print('')

if __name__ == '__main__':
    #train('./data/nlu_data.md', 'nlu_config.yml', './models/default')
    run()