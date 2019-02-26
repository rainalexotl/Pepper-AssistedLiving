# NLU

This is the main NLU and primary bot that runs when the robot is idling (i.e. not in proactive mode).

Intents are determined via a trained RASA NLU neural network, with intents forwarded to the correct secondary bot so that they can respond appropriately.

Secondary bots may 'lock' te conversation so that subsequent responses from the user are handled by the correct bot, and not subject to the intent prediction of the primary bot.

## Dependencies

You will require RASA NLU to run the primary bot, along with Spacy, for Python 2 and 3. The most notable python dependencies are:
``
aiml==0.9.2
future==0.17.1
rasa-nlu==0.14.3
sklearn-crfsuite==0.3.6
spacy==2.0.18
virtualenv==16.2.0
```

## Interfacing with the Primary Bot

The main bot listens on Port 3002 for text strings. Sample code to send messages to the main bot is in ``client_simulate.py``.
