from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import json

from rasa_nlu.training_data import load_data

from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer, Metadata, Interpreter
from rasa_nlu import config

def train (data, config_file, model_dir):
    training_data = load_data(data)
    configuration = config.load(config_file)
    trainer = Trainer(configuration)
    trainer.train(training_data)
    #model_directory = trainer.persist(model_dir, fixed_model_name = 'chat')

def run():
    interpreter = Interpreter.load('./models/default')

    result = interpreter.parse('I love oranges')

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

if __name__ == '__main__':
    #train('./data/nlu_data.md', 'nlu_config.yml', './models/default')
    run()