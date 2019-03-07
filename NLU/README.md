# NLU + Bots

This is the main NLU and primary bot that responds to user queries within its purview.

Intents are determined via a trained RASA NLU neural network, with intents forwarded to the correct secondary bot so that they can respond appropriately.

Secondary bots may 'lock' the conversation so that subsequent responses from the user are handled by the correct bot, and not subject to the intent prediction of the primary bot.

## Dependencies

You will require RASA NLU to run the primary bot, along with Spacy, for Python 2 and 3. The most notable python dependencies are:
```
aiml==0.9.2
future==0.17.1
rasa-nlu==0.14.3
sklearn-crfsuite==0.3.6
spacy==2.0.18
virtualenv==16.2.0
```

## Interfacing with the Primary Bot

The main bot listens on Port 3003 for text strings. Sample code to send messages to the main bot is in ``client_simulate.py``.

## Starting Up

Assuming dependencies are already installed, the main bot can be started simply with ``python bot.pyy``. Python 2 is preferable, and so if it is not the default in your environment, start with ``python2 bot.py`` instead.

Note that the profile system MUST be running for the bot to start, so make sure you run that from the ``Profiler`` directory with ``npm start``.

## Shutting Down

The main program, ``bot.py`` and its sub-programs, can be shutdown by sending ``@SHUTDOWN@`` to its input socket. This will also automatically shutdown the profile system using an internal message from the bot to the API.