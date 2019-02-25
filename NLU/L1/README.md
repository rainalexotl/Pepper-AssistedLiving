# NLU Level 1

This is the first level of NLU that runs when the robot is idling (i.e. not in proactive mode).

Intents are determined via a trained RASA NLU neural network, with intents forwarded to the correct Level 2 bot so that they can respond appropriately.

Level 2 bots may 'lock' te conversation so that subsequent responses from the user are handled by the correct bot, and not subject to the intent prediction of the Level 1 bot.