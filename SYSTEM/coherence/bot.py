#!/usr/bin/env python3

import copy
import random
import re
import traceback
from argparse import ArgumentParser
from hashlib import md5

import utils.log
import yaml
from flask import Flask, request
from flask_restful import Api
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from utils.abstract_classes import Bot
from utils.dict_query import DictQuery
from utils.filter import SentenceFilter

import data.drivers as D
import data.intro as I
from names.extract import NameExtractor

app = Flask(__name__)
api = Api(app)

BOT_NAME = 'coherence_bot'
VERSION = utils.log.get_short_git_version()
BRANCH = utils.log.get_git_branch()
logger = utils.log.get_logger(BOT_NAME + '-' + BRANCH)

RAPPORT_RULE_FILE = 'data/script.yaml'

ASR_CONFIDENCE = 0.02
ADVERTISEMENT_PROBABILITY = 0.3
RAPPORT_TURN_THRESHOLD = 3
MULTITURN_TURN_THRESHOLD = 1
ASR_RESPONSES = [
    'I am not sure I heard you right. Could you repeat that please?',
    'I am sorry I got distracted. Could you repeat that please?'
]
INCOMPL_UTT_RESPONSES = [
    "That's OK, it's a tough question. I can just wait a bit. Please try again.",
    "That's fine. Take your time.",
    "I know, it's not an easy question. Take your time.",
]

UNKNOWN_UTT_RESPONSES = [
    "That's OK, it's a tough question. ",
    "That's fine. ",
    "I know, it's not an easy question. ",
    "No problem. "
]


def is_low_confidence_asr(asr_hyps):
    if not asr_hyps:
        return False
    low_confidence = asr_hyps[0]['confidence'] < ASR_CONFIDENCE
    return low_confidence


class CoherenceData:
    """This just holds all the drivers & patterns so we don't need to load them every time.
    Everything is read-only, so threads shouldn't be an issue."""
    _instance = None

    def __init__(self):
        self._load_drivers()
        self._load_rapport()
        self.sentiment = SentimentIntensityAnalyzer()
        self.filter = SentenceFilter({'profanities': True})
        self.name_extractor = NameExtractor()

    def _load_drivers(self):
        self.drivers = {}
        for key, val in D.drivers.items():
            self.drivers[key] = {md5(text.encode('utf-8')).hexdigest(): text for text in val}

    def _load_rapport(self):
        try:
            with open(RAPPORT_RULE_FILE, 'r') as stream:
                self.rapport = yaml.load(stream)
        except yaml.YAMLError as exc:
            logger.critical(exc)

    @classmethod
    def get_instance(cls):
        """Get the instance of CoherenceData -- initialize on first use, the just return the value."""
        if not cls._instance:
            cls._instance = CoherenceData()
        return cls._instance


class CoherenceBot(Bot):
    def __init__(self):
        super(CoherenceBot, self).__init__(bot_name=BOT_NAME, bot_version=VERSION)
        # this will only create the object the first time it's used
        self.data = CoherenceData.get_instance()

        # Putting weights as placeholders here. At the moment it uses random.shuffle
        self.driver_category_probabilities = {
            self._get_preference_driver: 0.33,
            self._get_rapport_driver: 0.33,
            self._get_multiturn_driver: 0.34
        }

    def get(self):
        pass

    def post(self):
        print('\n')
        try:
            return self._get_answer(DictQuery(request.get_json(force=True)))
        except Exception:
            exc_message = traceback.format_exc(chain=False)
            logger.critical(exc_message)
            return {"traceback": exc_message}, 500, {'Content-Type': 'application/json'}

    def _get_answer(self, request_data):
        nlu_data = DictQuery(request_data.get('current_state.state.nlu.annotations'))

        # Reset the locking
        self.response.lock_requested = False

        question = nlu_data.get('processed_text', '')
        intent = nlu_data.get('intents', {}).get('intent')
        intent_param = nlu_data.get('intents', {}).get('param')
        topic = nlu_data.get('topics')
        postags = nlu_data.get('postag')
        nes_in_q = bool(list(nlu_data.get('entity_linking', {}).keys()) or
                        list(y for x in nlu_data.get('ner', {}).values() for y in x))
        self.response.bot_params = request_data.get('current_state.state.bot_states', {}).get(BOT_NAME, {}).get(
            'bot_attributes', {})
        self.user_attributes = request_data.get('user_attributes', {})
        turn = int(request_data.get('current_state.state.turn_no'))
        last_bot = request_data.get('current_state.state.last_bot')
        last_state = request_data.get('history')
        last_state = DictQuery(last_state[-1]) if last_state else None
        last_response = next(iter(last_state.get('state.response', {'': None}).values())) if last_state else None
        last_intent = last_state.get('state.nlu.annotations.intents.intent') if last_state else None
        asr_hyps = request_data.get('current_state.state.input.hypotheses', [])
        self.session_id = request_data.get('current_state.session_id')

        # Check if a rapport driver was used in the last turn
        if last_bot == BOT_NAME and self.response.bot_params.get('driver_type') == 'RAPPORT':
            self.response.bot_params['rapport_last_turn'] = turn - 1

        # Check whether the asr confidence is sufficient enough to process the utterance
        # but do not do it 2 times in a row
        if is_low_confidence_asr(asr_hyps) and last_response not in ASR_RESPONSES:
            self.response.result = random.choice(ASR_RESPONSES)
            self.response.lock_requested = True
        else:
            if not self.response.result:
                # try intro (will return nothing on later turns)
                self.response.result = self.get_intro_response(question, turn, intent, intent_param,
                                                               last_bot, last_intent, topic, postags)
            # try handling builtin intents
            if not self.response.result:
                self.response.result = self.handle_intents(intent, intent_param, question, turn, topic,
                                                           last_bot, last_response, last_intent, postags, nes_in_q)
            if self.response.result:
                # if we have intro/intent response, we should lock
                self.response.lock_requested = False
            else:
                # always offer a driver
                self.response.result = self.get_driver(question, turn, last_bot, topic, intent, intent_param)

        result = self.response.toJSON()
        result['user_attributes'] = self.user_attributes

        logger.debug("Bot Params: {}".format(self.response.bot_params))

        return [result]

    def handle_intents(self, intent, intent_param, question, turn, topic,
                       last_bot, last_response, last_intent,
                       postags, nes_in_q):
        """Handle some of the built-in intents (service turns): offer drivers for topics,
        handle repeats, stop intent."""

        if intent == 'repeat':
            return ('I said, ' + re.sub(r'^I said, ', '', last_response)
                    if last_response
                    else 'I did not say anything.')

        elif intent == 'stop':
            return ('STOP INTENT REQUESTED'
                    if last_intent == 'stop'

                    else '<say-as interpret-as="interjection">Aww.</say-as>. You want to stop? But I love talking with you. And I can talk more about movies or '
                         'music. But if you really want to, please just say the single word stop')

        elif intent == 'dont_tell_about' or intent == 'negative_preference':
            self.append_to_user_dislikes(intent_param)

            # Also remove it from the list of preferences
            try:
                pref = self.user_attributes.get('preferences', [])
                if intent_param in pref:
                    pref.remove(intent_param)
            except Exception as e:
                logger.exception("error in preference removal")
            return self.get_driver(question, turn, last_bot, intent=intent, topic='change',
                                   intent_param=intent_param)

        elif intent == 'tell_me_about' or intent == 'positive_preference':
            # only lock if the user actually says "tell me about movies" etc.,
            # i.e. there are no named entities but a topic was recognized (for which we have drivers)
            # do not lock for "tell me about star trek" and the like
            self.append_to_user_preferences(intent_param)

            # Also remove it from the list of dislikes
            try:
                pref = self.user_attributes.get('dislikes', [])
                if intent_param in pref:
                    pref.remove(intent_param)
            except Exception as e:
                logger.exception("error in dislike removal")

            if (topic and (not nes_in_q or intent_param == topic) and self.data.drivers.get(
                    topic)) or topic == 'change':
                # prepend advertisement driver if the user wants to change topic
                if topic == 'change':
                    return self._add_advertisement_driver(prepend=True) + self.get_driver(question, turn, last_bot,
                                                                                          topic, intent, intent_param)
                else:
                    return self.get_driver(question, turn, last_bot, topic, intent, intent_param)

        elif intent == 'name':
            return self.handle_name_intent(question, intent_param, turn,
                                           last_bot, last_intent, topic, postags)
        elif intent == 'time':
            # TODO
            return None

        elif intent == 'forget_me':
            self.user_attributes = {'empty': 'empty'}
            return 'All current user data deleted.'

        elif intent == 'incomplete_utterance':
            return random.choice(INCOMPL_UTT_RESPONSES) + self._add_advertisement_driver(force=True)

        elif intent == 'donot_know' and intent_param == 'my name':
            if 'user_name' in self.user_attributes:
                return 'Your name is %s, right?' % self.user_attributes['user_name']
            return 'I\'m sorry, I don\'t know your name yet. What is your name?'

        return None

    def handle_name_intent(self, question, intent_param, turn, last_bot, last_intent, topic, postags):
        # Extract the name
        try:
            name = self.data.name_extractor.extract_name(intent_param, postags)
        except TypeError:
            name = ''
        user_asks_for_name = self.data.name_extractor.user_asks_for_name(question)

        # we were not able to extract the name
        if not name:
            # we were repeatedly not able to extract the name
            if last_intent == 'name' and 'user_name' not in self.user_attributes:
                return ('I\'m sorry but I wasn\'t able to catch your name. ' +
                        self.get_driver(question, turn, last_bot, topic))
            # this is the 1st time we couldn't get the name -- ask for it second time
            if 'user_name' in self.user_attributes:  # delete any previous name
                if len(self.user_attributes) > 1:
                    del self.user_attributes['user_name']  # delete name but keep other attributes in place
                else:
                    self.user_attributes = {'empty': 'empty'}  # force reset
            return 'I\'m sorry I didn\'t catch your name. What should I call you?'

        # we were able to get the name + it contains no profanities -- save the name + reply nicely
        elif self.data.filter.check_sentence(name):
            # the name is still the same (and user doesn't try to repeat it)
            if self.user_attributes.get('user_name') == name and last_intent != name:
                return (random.choice(I.response_turn_3_2_known_name) + ". " +
                        self.get_driver(question=question, function=self._get_multiturn_driver, turn=turn))
            self.user_attributes = {}
            self.user_attributes['user_name'] = name
            return (random.choice(I.response_turn_3_1_p) + "*username*. " +
                    ('I\'m sorry but I can\'t disclose my name at this time. ' if user_asks_for_name else '') +
                    (random.choice(I.response_turn_3_2) if turn < 3 else '') +
                    # self.get_driver(question, turn, last_bot, topic))
                    self.get_driver(question=question, function=self._get_multiturn_driver, turn=turn))

        # Don't feedback or save the username if it contains profanity
        # -- let the profanity bot take over
        return None

    def append_to_user_dislikes(self, dislike):
        try:
            pref = self.user_attributes.get('dislikes', [])
            logger.info('adding {} to list of dislikes'.format(dislike))
            pref.extend([x for x in self.data.drivers.keys() if x in dislike])
            self.user_attributes['dislikes'] = list(set(pref))
        except TypeError:
            logger.exception("Error in appending dislike")

    def append_to_user_preferences(self, preference):
        try:
            pref = self.user_attributes.get('preferences', [])
            logger.info('adding {} to list of preferences'.format(preference))
            pref.extend([x for x in self.data.drivers.keys() if x in preference])
            self.user_attributes['preferences'] = list(set(pref))
        except TypeError:
            logger.exception("Error in appending preference")

    def get_driver(self, question,
                   turn=None,
                   last_bot='',
                   topic=None,
                   intent=None,
                   intent_param=None,
                   function=None):
        """Return random element from a list, but avoid repeating the same stuff for the same
        session ID. For two-level structures, samples a substructure and gets a random element.
        Remembers that the structure was last used for the session"""
        # changed_topic_turn = topic_from_bot.get('topic_change_turn')
        # preferences = user_attributes.get('user_attributes['preferences']', [])
        logger.info("SESSION ID: {}".format(self.session_id))
        logger.info("INPUT: {}".format(question))
        logger.info("USER DATA: {}".format(self.user_attributes))

        res = ''
        if not last_bot:
            last_bot = ''

        # if the topic hasn't changed this turn, use the last saved topic
        if not topic:
            topic = self.response.bot_params.get('topic') if self.response.bot_params.get('topic') != 'change' else None
            restored_topic = True
        else:
            restored_topic = False

        logger.info("topic: {}, pref: {}, is_first_turn: {}".format(topic, self.user_attributes.get('preferences'),
                                                                    self.response.bot_params.get('is_first_turn')))

        # If something needs to forcefully call a specific driver category/function
        if function:
            print(function)
            res = function(topic=topic, turn=turn, question=question, intent=intent, intent_param=intent_param)

        # Stick to rapport if we've already asked a question from there
        if not res and self.response.bot_params.get('is_first_turn') is False:
            logger.info("RAPPORT MULTITURN")
            res = self._get_rapport_driver(question=question, intent=intent, intent_param=intent_param, turn=turn)
            self.response.bot_params['driver_type'] = 'RAPPORT'

        # Check whether we have a mt_driver staged to continue, unless the user specifically asks to
        # talk about a topic (thus not restoring the previous topic but getting it from the NLU)
        if not res and self.response.bot_params.get('mt_staged') and topic != 'change' and restored_topic:
            res = self._get_multiturn_driver(turn=turn, topic=topic, restored_topic=restored_topic)

        # we have a topic and some drivers for it
        if not res:
            res = self._get_topic_driver(topic=topic, last_bot=last_bot, turn=turn, restored_topic=restored_topic)

        # If not topic, check if we are in the middle of a chitchat dialogue (unless the user want's to change topic
        if not res and self.response.bot_params.get('mt_staged') and topic != 'change':
            driver_func = [self._get_multiturn_driver]
        else:
            # Pick preference, rapport or chitchat driver category at random
            driver_func = random.sample(list(self.driver_category_probabilities.keys()),
                                        len(list(self.driver_category_probabilities.keys())))
        if not res:
            for f in driver_func:
                res = f(topic=topic, turn=turn, question=question, intent=intent, intent_param=intent_param, restored_topic=restored_topic)
                if res:
                    logger.debug("Roll selected {}".format(f.__name__))
                    break

        # Since some functions return more than one result split them
        if isinstance(res, tuple):
            topic = res[1]
            res = res[0]

        # try generic drivers
        if not res:
            res = self._get_generic_driver()

        logger.info('OUT: %s', res)

        if '*driver*' in res:
            res = res.replace('*driver*', self.get_driver(question,
                                                          turn=turn,
                                                          topic=topic,
                                                          last_bot=last_bot,
                                                          intent=intent,
                                                          intent_param=intent_param))

        # Save the response to the bot_attributes to be retrieved during postprocessing (since response.result still
        # needs to be from the bot that requested the driver
        self.response.bot_params['driver'] = res

        # Also expose a driver for unhandled user utterance in case coherence is the only candidate
        # self.response.bot_params['unhandled_driver'] = random.choice(D.unhandled_drivers)

        # Also save the current topic to retain between turns if not updated by the nlu
        self.response.bot_params['topic'] = topic

        # Prepend unknown driver on cant_think/donot_know intents
        if intent == 'cant_think' or intent == 'donot_know':
            res = random.choice(UNKNOWN_UTT_RESPONSES) + res

        logger.info("Driver category: {}".format(self.response.bot_params.get('driver_type')))

        return res

    def _get_topic_driver(self, **kwargs):
        # print("t",kwargs)
        # we have a topic and some drivers for it
        if kwargs.get('topic') is not None and kwargs.get('topic') != 'change' and kwargs.get(
                'topic') in self.data.drivers and kwargs.get('topic') not in self.user_attributes.get(
                'dislikes', []):
            # Skip topic driver every 3 driver's used
            if self.response.bot_params.get('topic_skipped') is not True and \
                    len(self.response.bot_params.get('used_drivers', {}).get(kwargs.get('topic'), [1])) % 3 == 0:
                logger.info('Skipping topic driver...')
                self.response.bot_params['topic_skipped'] = True
                return None
            else:
                # res = self._get_random_norepeat_driver(kwargs.get('topic'))
                res = self._get_multiturn_driver(topic=kwargs.get('topic'), turn=kwargs.get('turn'))
                self.response.bot_params['topic_skipped'] = False
            # we have an unused driver for the topic
            if res:
                # If the topic was changed in the same turn as the driver selected
                # if changed_topic_turn == turn or last_bot.startswith('intro'):
                #    pass
                # back to "topic"...
                if not kwargs.get('last_bot') == BOT_NAME and kwargs.get('topic'):
                    res = random.choice(D.prefix) + kwargs['topic'] + ". " + res
                    # do not repeat "So," in the driver if it's in the prefix
                    res = re.sub(r'^(So|Anyway)(,? )(.*)\. So,? ', r'\1\2\3. ', res, re.I)
                # this means we're asking another driver question in the row for the same topic
                # --> add some meaningless response to appear we take notice
                else:
                    res = random.choice(D.platitudes) + " " + res
            self.response.bot_params['driver_type'] = 'TOPIC'
            return res
        else:
            return None

    def _get_preference_driver(self, **kwargs):
        res = None
        topic = None
        # try drivers for user_attributes['preferences'] (if any)
        random.shuffle(self.user_attributes.get('preferences',
                                                []))  # First randomize the user_attributes['preferences'] order so we don't always get the 1st one
        for preference in self.user_attributes.get('preferences', []):
            if res:  # stop as soon as we found a driver
                break
            if preference in self.data.drivers and preference not in self.user_attributes.get('dislikes',
                                                                                              []):  # we have drivers for this preference
                logger.info('PREF: %s', preference)
                try:
                    if kwargs.get('topic') == 'change' and self.response.bot_params.get(
                            'topic') and preference in self.response.bot_params.get('topic'):
                        continue
                except Exception as e:
                    logger.exception("Oops!")

                res = self._get_multiturn_driver(topic=preference)
                if res:
                    # history.set_topic(sessionID, preference, turn)  # Set the selected preference as the current topic
                    topic = preference
                    self.response.bot_params['topic_change_turn'] = kwargs.get('turn')
                    self.response.bot_params['driver_type'] = 'PREFERENCE'
                    # if changed_topic_turn != turn:
                    res = random.choice(D.pref_prefix) + preference + ", " + res
        return res, topic

    def _get_generic_driver(self):
        driver, _ = self._get_random_norepeat_driver('GENERIC', repeat_all=True)
        res = self._add_advertisement_driver() + driver
        try:
            topic_choices = random.sample(
                [x for x in D.common_topics if x not in self.user_attributes.get('dislikes', [])], 3)
            res = res.format(pref1=topic_choices[0], pref2=topic_choices[1], pref3=topic_choices[2])
        except ValueError:
            while True:
                driver, _ = self._get_random_norepeat_driver('GENERIC', repeat_all=True)
                res = self._add_advertisement_driver() + driver
                if '{pref' not in res:
                    break
        self.response.bot_params['driver_type'] = 'GENERIC'
        return res

    def _get_multiturn_driver(self, **kwargs):
        # print("m",kwargs)
        mt_driver_text = ''
        topic = kwargs.get('topic') if kwargs.get('topic') else 'MULTITURN'
        try:
            # If we are not in a multiturn script already if chitchat wasn't selected for X turns, reset mt tracker
            print(self.response.bot_params)
            if not self.response.bot_params.get('mt_staged') or not self.response.bot_params.get('mt_staged', [None, None, None])[0] or \
                            kwargs.get('turn', 0) > int(self.response.bot_params.get('chitchat_last_turn', 0)) + MULTITURN_TURN_THRESHOLD or \
                            not kwargs.get('restored_topic'):

                # Reset multiturn tracker
                self.response.bot_params['mt_staged'] = [None, None, None]
                # Get a new mt driver and use the first bit (driver's id is already set by _get_random_norepeat_driver)
                res, driver_code = self._get_random_norepeat_driver(topic)
                if not res:
                    return ''
                # [full driver, current part, part's index]
                self.response.bot_params['mt_staged'] = [driver_code, res.split('~~')[0], 0]
                res = res.split('~~')[0]
                self.response.bot_params['chitchat_last_turn'] = kwargs.get('turn', 0)
                return self.check_and_split_mt_driver(res)
            else:
                # Get the entire last used mt driver text
                try:
                    for t, v in self.data.drivers.items():
                        for h, d in v.items():
                            if h == self.response.bot_params['mt_staged'][0]:
                                mt_driver_text = d
                                print(d)
                                break

                    # mt_driver_text = self.data.drivers[kwargs.get('topic')][self.response.bot_params['mt_staged'][0]]
                    used_part = self.response.bot_params['mt_staged'][1]
                except KeyError:
                    exc_message = traceback.format_exc(chain=False)
                    logger.critical("SessionID: " + exc_message)
                    # If the staged driver is for another topic, return and let the rest of the coherence pipeline to run
                    self.response.bot_params['mt_staged'] = [None, None, None]
                    return ''

                # Return the next part of the multiturn driver
                mt_driver = mt_driver_text.split('~~')
                try:
                    next_part = mt_driver[mt_driver.index(used_part) + 1]
                    self.response.bot_params['mt_staged'] = [self.response.bot_params['mt_staged'][0], next_part,
                                                             mt_driver.index(next_part)]
                    self.response.bot_params['chitchat_last_turn'] = kwargs.get('turn', 0)
                    logger.info('Continuing chitchat...')
                    return self.check_and_split_mt_driver(next_part)
                except IndexError:
                    # If no next part -> reset multiturn tracker
                    self.response.bot_params['mt_staged'] = [None, None, None]
                    return ''
        except Exception:
            exc_message = traceback.format_exc(chain=False)
            logger.critical("SessionID: "+ exc_message)
            return ''

    def check_and_split_mt_driver(self, sentence):
        """Checks if an unhandled driver is incorporated to the driver segment and sets it accordingly"""
        s = sentence.split('|')
        if len(s) > 1:
            self.response.bot_params['unhandled_driver'] = s[0]
            return s[1]
        else:
            return s[0]

    def _get_random_norepeat_driver(self, topic, repeat_all=False):
        # determine which drivers were not used so far
        used_drivers = self.response.bot_params.get('used_drivers', {})
        try:
            avail_drivers = set(self.data.drivers.get(topic if topic else 'MULTITURN').keys()) - set(used_drivers.get(topic, []))
        except AttributeError:
            logger.info("Topic {} was unknown in coherence. Using MULTITURN instead".format(topic))
            topic = 'MULTITURN'
            avail_drivers = set(self.data.drivers.get(topic).keys()) - set(used_drivers.get(topic, []))
        if not avail_drivers:
            if repeat_all:  # reset drivers for the topic -- they will be repeated
                avail_drivers = set(self.data.drivers.get(topic if topic else 'MULTITURN').keys())
                used_drivers[topic] = []
            else:
                return None, None
        # choose the next driver
        driver_id = random.choice(list(avail_drivers))
        # remember it was used in bot_params
        used_drivers[topic] = used_drivers.get(topic, []) + [driver_id]
        self.response.bot_params['used_drivers'] = used_drivers
        # keep track of mt driver's id selected
        # self.response.bot_params['mt_staged'] = [driver_id, None, None]
        # return driver text
        return self.data.drivers.get(topic if topic else 'MULTITURN')[driver_id], driver_id

    def _add_advertisement_driver(self, force=False, prepend=False):
        if force:
            return random.choice(D.advertising_drivers)

        # Append advertisement driver based on probability
        if random.random() <= ADVERTISEMENT_PROBABILITY:
            return random.choice(D.advertising_drivers) if not prepend \
                else random.choice(D.advertising_drivers).replace('Also,', '')  # TODO use regex here
            # Then remove possible platitudes (it just sounds weird...)
            # TODO
        else:
            return ''

    def _get_rapport_driver(self, **kwargs):  # question, turn=None, intent=None, intent_param=None):
        response = ''
        if self.response.bot_params.get('is_first_turn') is not False and (
                    kwargs.get('turn') < int(self.response.bot_params.get('rapport_last_turn', 0)) +
                    RAPPORT_TURN_THRESHOLD):
            logger.info("Bypassing rapport")
            return None
        else:
            # Continue with rest of the function
            logger.info("ADDING RAPPORT DRIVER")
            self.response.bot_params['driver_type'] = 'RAPPORT'

        # If it's the first time for this session, initialize the questions order
        try:
            remaining_questions = self.response.bot_params['rapport_q_order']
        except KeyError:
            logger.info('Initialising rapport questions')
            random.shuffle(self.data.rapport)
            self.response.bot_params['rapport_q_order'] = copy.deepcopy(self.data.rapport)
            self.response.bot_params['is_first_turn'] = True
            remaining_questions = self.response.bot_params.get('rapport_q_order', {})

        logger.info('Remaining questions: %s', str(len(remaining_questions)))
        if self.response.bot_params.get('is_first_turn') != False:
            q = self.response.bot_params.get('rapport_staged')  # history.get_rapport_staged(sessionID)
            logger.info("Staged question: %s", q)
            if not q or q == 'EMPTY':
                try:
                    q = remaining_questions.pop()
                except IndexError:  # we have no more questions to ask
                    logger.info("No more rapport questions to ask")
                    self.response.bot_params['rapport_staged'] = 'EMPTY'
                    self.response.lock_requested = False
                    return ''
                self.response.bot_params['rapport_q_order'] = remaining_questions
                self.response.bot_params['rapport_staged'] = q

            self.response.bot_params['is_first_turn'] = False
            response = random.choice(D.question_prefix) + q['question']
        else:
            staged_q = self.response.bot_params.get('rapport_staged', 'EMPTY')
            logger.debug("staged %s", staged_q)
            if staged_q != 'EMPTY':  # not first turn & staged == we asked a question in previous turn
                for option in staged_q['options']:
                    # print('<<<<', intent, option['preference'])
                    if option['preference'] == 'open':
                        # If it is an open rapport question consider it answered regardless of the response
                        self.response.bot_params['rapport_staged'] = 'EMPTY'
                        break
                    elif option['preference'] == 'both' and re.search(option['pattern'], kwargs.get('question'), re.I):
                        self.response.lock_requested = True

                        # Remove the question since it was answered
                        self.response.bot_params['rapport_staged'] = 'EMPTY'
                        response = option['response']

                        # Append this answer to the list of user's user_attributes['preferences'] in the db
                        for o in staged_q['options']:
                            if o['preference'] != 'both' and o['preference'] != 'none':
                                self.append_to_user_preferences(o['preference'])
                        break
                    elif option['preference'] == 'none':
                        if re.search(option['pattern'], kwargs.get('question'),
                                     re.I) or kwargs.get('intent') == 'negative_preference' or kwargs.get('intent') == 'dont_tell_about':
                            self.response.lock_requested = True

                            if kwargs.get('intent') == 'negative_preference' or kwargs.get(
                                    'intent') == 'dont_tell_about':
                                # Append this answer to the list of user's user_attributes['dislikes'] in the db
                                self.append_to_user_dislikes(kwargs.get('intent_param'))

                            # Remove the question since it was answered
                            self.response.bot_params['rapport_staged'] = 'EMPTY'
                            response = option['response']
                            break
                    elif re.search(option['pattern'], kwargs.get('question'),
                                   re.I) and not kwargs.get('intent') == 'dont_tell_about' and not kwargs.get('intent') == 'negative_preference':
                        self.response.lock_requested = True

                        # Remove the question since it was answered
                        self.response.bot_params['rapport_staged'] = 'EMPTY'
                        response = option['response']

                        # Append this answer to the list of user's user_attributes['preferences'] in the db
                        self.append_to_user_preferences(option['preference'])
                        break

                if not response:
                    self.response.bot_params['is_first_turn'] = True
                    self.response.lock_requested = False
                    self.response.bot_params['rapport_staged'] = 'EMPTY'
                    return ''  # return empty to let the bucket run its course
                self.response.bot_params['is_first_turn'] = True
                self.response.bot_params['rapport_staged'] = 'EMPTY'

            else:
                return ''

            response += '*driver*'
            # pp.pprint(response)
        return response

    def get_intro_response(self, utterance, turn, intent, intent_param,
                           last_bot, last_intent, topic, postags):
        try:
            # User responded with name
            if intent == 'name':  # this is what we get if the name intent matches
                return self.handle_name_intent(utterance, intent_param, turn,
                                               last_bot, last_intent, topic, postags)

            # How are you doing
            if turn == 1:
                if I.HOWAREYOU.search(utterance):
                    # fix sentence a bit so sentiment analyzer works properly
                    utterance = I.HOWAREYOU_NEGFIX1.sub(r'\1 not', utterance)
                    utterance = I.HOWAREYOU_NEGFIX2.sub(r'\1 \2 not', utterance)
                    utterance = I.HOWAREYOU_NEGFIX3.sub(r'not \1', utterance)
                    utterance = I.HOWAREYOU_FILLERFIX.sub(r'\1', utterance)

                    # select reaction based on sentiment
                    logger.info('Intro Fixed utterance: %s' % utterance)

                    # XXX TODO remove the sentiment classifier
                    sent_score = self.data.sentiment.polarity_scores(utterance)['compound']
                    logger.info('Sentiment %s' % sent_score)

                    if -0.1 <= sent_score <= 0.1:
                        resp = random.choice(I.response_turn_2_0)
                    elif sent_score >= 0:
                        resp = random.choice(I.response_turn_2_p)
                    else:
                        resp = random.choice(I.response_turn_2_n)

                    # check if we need to respond to how are you
                    if I.HOWAREYOU_BACK.search(utterance):
                        resp += ' ' + random.choice(I.response_turn_2_how)
                    if not self.user_attributes.get('user_name'):
                        resp += ' ' + random.choice(I.response_turn_2_name)
                    else:
                        resp += ' ' + random.choice(I.response_turn_2_known_name)
                    return resp
                return

            # we previously asked for name (and the user didn't provide it in the previous turn already)
            elif turn == 2 and last_intent != 'name':
                # user does not want to tell their name
                if (I.NONAME.search(utterance) or
                        ('user_name' not in self.user_attributes and I.NO.search(utterance))):
                    return (random.choice(I.response_turn_3_1_n) +
                            random.choice(I.response_turn_3_2) +
                            self.get_driver(question=utterance, function=self._get_multiturn_driver, turn=turn))
                # self.get_driver(utterance, turn, last_bot, topic, intent, intent_param))
                # We think we know who the user is and we try to confirm
                elif I.NO.search(utterance):
                    self.user_attributes = {'empty': 'empty'}  # Reset user attributes at this point
                    return random.choice(D.platitudes) + " " + random.choice(I.response_turn_2_name)
                elif I.YES.search(utterance) and not I.NO.search(utterance):
                    return (random.choice(I.response_turn_3_2_known_name) + ". " +
                            self.get_driver(question=utterance, function=self._get_multiturn_driver, turn=turn))
                    # self.get_driver(utterance, turn, last_bot, topic, intent, intent_param))
                # user said something unrelated
                else:
                    return

            # we asked for name after the user said it's not the same person as last time
            if turn == 3 and last_intent != 'name':
                # user does not want to tell their name
                if I.NONAME.search(utterance):
                    return (random.choice(I.response_turn_3_1_n) + ". " +
                            random.choice(I.response_turn_3_2) + ". " +
                            self.get_driver(question=utterance, function=self._get_multiturn_driver, turn=turn))
                            # self.get_driver(utterance, turn, last_bot, topic, intent, intent_param))
                # user said something unrelated
                else:
                    return

        except Exception as ex:
            logger.warn('Exception in intro: %s' % str(ex))
            return


api.add_resource(CoherenceBot, "/")

if __name__ == "__main__":
    argp = ArgumentParser()
    argp.add_argument('-p', '--port', type=int, default=5115)
    argp.add_argument('-l', '--logfile', type=str, default=BOT_NAME + '.log')
    argp.add_argument('-cv', '--console-verbosity', default='info', help='Console logging verbosity')
    argp.add_argument('-fv', '--file-verbosity', default='debug', help='File logging verbosity')
    args = argp.parse_args()
    utils.log.set_logger_params(BOT_NAME + '-' + BRANCH, logfile=args.logfile,
                                file_level=args.file_verbosity, console_level=args.console_verbosity)
    app.run(host="0.0.0.0", port=args.port, threaded=True)
