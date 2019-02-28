from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import aiml
import pkg_resources
import requests

matchmaking_strings = {"greet", "bye", "thank", "affirm"}

class chit_chat():
    def __init__(self):
        print('[BOTS/CHIT_CHAT] Starting...')