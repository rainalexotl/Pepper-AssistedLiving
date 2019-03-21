#!/usr/bin/env python3

import concurrent
import json
import random
import socket
import time
import uuid
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor

import requests
import utils.log
import yaml
from flask import Flask, request
from flask_restful import Api, Resource
from gunicorn.app.base import BaseApplication
from utils.abstract_classes import Response
from utils.dict_query import DictQuery
from utils.nlu_wrapper import NLUWrapper

from managers import db_wrapper
#from managers.db_wrapper import DynamoDBWrapper
from managers.mongo_wrapper import MongoDBWrapper
from managers.state import StateManager
from response_selection.filter import BatchFilter
from response_selection.selection_strategy import create_selection_strategy
from response_utils.postprocessor import Postprocessor
from timeit import timeit
from response_utils.emotional_model import EmotionalModel

VERSION = 'CACourse'
BRANCH = 'CACourse'
HOSTNAME = 'CACourse'

app = Flask(__name__)
api = Api(app)
logger = utils.log.get_logger("alana-" + BRANCH)

no_response_templates = [
    'I\'m afraid I didn\'t get that. *username*, could you repeat that please?',
    "I\'m so sorry *username* I get so many conversations at the same time. Could you repeat that please?"
]

@timeit
def call_module(url, data, timeout, module_name=''):
    """
    Function to call several modules in the architecture (e.g. bots, nlu pipeline, etc)
    :param url: the endpoint of the module to call
    :param data: the data to post
    :param timeout: the connection timeout
    :param module_name: module name (needed for logging purposes only)
    :return: the modules response in json format
    """
    try:
        if isinstance(data, str):
            res = requests.post(url, json=json.dumps(data), timeout=timeout)
        else:
            res = requests.post(url, json=data, timeout=timeout)

    except requests.Timeout:
        logger.warning("Connection timeout while calling %s (%s)" % (module_name, url))
        return None
    except requests.ConnectionError as exp:
        logger.warning("Error connecting to %s (%s): %s" % (module_name, url, str(exp)))
        return None

    if res.status_code != 200:
        if res.headers["content-type"] == "application/json":
            exp_json = res.json()
            if isinstance(exp_json, dict) and "traceback" in exp_json:
                error_text = exp_json["traceback"]
            else:
                error_text = json.dumps(exp_json)
        else:
            error_text = res.text
        logger.critical("Error while calling %s (%s) - HTTP status code %d\n%s" %
                        (module_name, url, res.status_code, error_text))

        return None

    return res.json()


def format_linker_info(linker_data):
    def cond_move(src_dict, target_dict, key):
        if key in src_dict:
            target_dict[key] = src_dict[key]

    linker_info = {}

    try:
        for span, entity in linker_data.items():
            if isinstance(entity, list):
                linker_info[span] = []
                for ent_var in entity:
                    linker_info[span].append(
                        {
                            "identifier": ent_var["entityLink"]["identifier"],
                            "entity": ent_var["entity"]
                        }
                    )
                    cond_move(ent_var, linker_info[span][-1], "score")
                    cond_move(ent_var, linker_info[span][-1], "age")
            else:
                linker_info[span] = {
                    "identifier": entity["entityLink"]["identifier"],
                    "entity": entity["entity"]
                }
                cond_move(entity, linker_info[span], "score")
                cond_move(entity, linker_info[span], "age")
    except:
        logger.error('Cannot format linker data %s' % str(linker_data))
        return linker_data

    return linker_info


class AlanaMain(Resource):

    def __init__(self, **kwargs):
        self.config = kwargs.get("config")
        state_table = MongoDBWrapper('StateTable')
        user_table = MongoDBWrapper('UserTable')
        self.state_manager = StateManager(state_table, user_table,
                                          self.config.HISTORY_CHUNK_LENGTH)
        self.ranker = kwargs.get("ranker")
        self.postprocessor = kwargs.get("postprocessor")
        self.bucket_filter = kwargs.get("bucket_filter")
        self.emotional_model = kwargs.get("emotional_model")
        self.nlu_wrapper = NLUWrapper(host=self.config.SERVICES["nlu"].rsplit(':', 1)[0].rsplit("/", 1)[1])
        # Initialise a new resource for each request
        # a specific session is created for each request.
        # Adapted from: https://boto3.readthedocs.io/en/latest/guide/resources.html#multithreading-multiprocessing

    def get(self):
        pass

    def post(self):
        request_data = request.get_json(force=True)
        request_data = DictQuery(request_data)

        return self.get_answer(session_id=request_data.get('session_id'),
                               asr_hypotheses=request_data.get('asr_hypotheses'),
                               text=request_data.get('question'),
                               timestamp=request_data.get('timestamp'),
                               user_id=request_data.get('user_id'),
                               debug_info_requested=request_data.get('request_debug_info', False))
    @timeit
    def get_answer(self,
                   event=None,
                   session_id='CLI-%s' % time.strftime('%Y-%m-%d--%H-%M-%S'),
                   asr_hypotheses=None,
                   text=None,
                   timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                   user_id='dummy-user',
                   debug_info_requested=False,
                   ):
        """
        The main exposed function to the lambda function. Can either get as input an ASK event of individual
        attributes (e.g. if lambda function extract these or for CLI
        """
        # Create the state object from input + db
        if isinstance(event, dict):
            event = DictQuery(event)
            self.state_manager.prepare_state(event)
        else:
            self.state_manager.prepare_state_from_external(session_id=session_id, text=text, user_id=user_id,
                                                           timestamp=timestamp,
                                                           hypotheses=asr_hypotheses,
                                                           hostname=HOSTNAME, hub_version=VERSION)
        logger.info("\n\n")
        logger.info("--------- Current turn ----------")
        logger.info("Session ID: %s  Timestamp %s  Host %s  Version %s" %
                    (session_id, timestamp, HOSTNAME, VERSION))
        logger.info("System emotional state: {}".format(self.emotional_model.em_state))
        logger.info("Input text: %s" % text)
        if asr_hypotheses:
            logger.debug("Avg ASR token confidence score: %g" %
                         (sum(asr_hypotheses[0]['token_conf']) / len(asr_hypotheses[0]['token_conf'])))
            logger.debug("Min ASR token confidence score: %g" % min(asr_hypotheses[0]['token_conf']))
            logger.info("Amazon ASR confidence score: %g" % asr_hypotheses[0]["confidence"])
            logger.debug("ASR hypotheses:\n" +
                         "\n".join(["-- [%.3f]:  " % hyp['confidence'] +
                                    "  ".join(["%s %.3f" % (tok, conf)
                                               for tok, conf in zip(hyp['tokens'], hyp['token_conf'])])
                                    for hyp in asr_hypotheses]))
        else:
            logger.info("No ASR information in chat-based mode.")

        # Forward data to the NLU pipeline (https://github.com/WattSocialBot/mercury-nlu/blob/master/notes.md)
        history = self.state_manager.get_history(self.state_manager.current_state.get('session_id'))
        user_attributes = self.state_manager.get_user_attributes(self.state_manager.current_state.get('user_id'))
        logger.debug("User attributes: %s" % str(user_attributes))

        # Run RegexClassifier on each item on the n-best list
        if asr_hypotheses:
            for candidate, score in self.state_manager.hypotheses_list:
                nlu_data = DictQuery(self.nlu_wrapper.annotate(candidate, modules=['Preprocessor', 'RegexIntents', 'PersonaRegexTopicClassifier']))
                if nlu_data and nlu_data.get('annotations.intents.intent') and \
                        not nlu_data.get('annotations.intents.intent') == 'stop':
                        # self.state_manager.hypotheses_list[0][1] - score < 0.2:
                    # Just to notify us if an alternative was found
                    if self.state_manager.hypotheses_list.index((candidate, score)) > 0:
                        logger.debug("Alternative intent found: {}".format(nlu_data.get('annotations.intents.intent')))
                    self.state_manager.text = candidate
                    break

        nlu_data = {
            "state": {
                "utterance": self.state_manager.text,
                "context": {
                    "current_state": self.state_manager.current_state
                }
            }
        }

        if history:
            nlu_data["state"]["context"]["history"] = history

        if user_attributes:
            nlu_data["state"]["context"]["user_attributes"] = user_attributes

        nlu_annotations = call_module(self.config.SERVICES["nlu"], nlu_data, self.config.BOT_TIMEOUT, module_name='NLU')

        # we can only continue if NLU worked
        if nlu_annotations is not None:
            logger.debug("Executed NLU modules: %s", ",".join(nlu_annotations["modules"]))

            # Update state with NLU annotations
            self.state_manager.add_annotations_to_state(nlu_annotations)
            logger.info("Linker: {}".format(
                format_linker_info(nlu_annotations["annotations"].get('entity_linking', {}))
            ))
            logger.info("Topic: {}".format(nlu_annotations['annotations'].get('topics')))
            logger.info("Intents: {}".format(nlu_annotations['annotations'].get('intents')))
            logger.info("Multi-turn intents: {}".format(nlu_annotations['annotations'].get('multi_turn_intents')))
            logger.info("NPs: {}".format(nlu_annotations['annotations'].get('nps')))
            logger.info("Bot NER: {} / user NER: {}".format(
                nlu_annotations['annotations'].get('bot_ner'), nlu_annotations['annotations'].get('ner')))
            logger.info("Processed text: {}".format(nlu_annotations['annotations'].get('processed_text', '')))
            # logger.info("--------------------------------")

            # Forward state to bot ensemble
            bucket = self.call_bots(self.state_manager.current_state, history=history, user_attributes=user_attributes)

        # NLU fail -- can't call bots, just go to empty bucket
        else:
            bucket = None

        # Send populated bucket to the selection strategy module to pick a response
        # Since now coherence_bot is being called on each turn, but only written to the db if used, if no other
        # bot has a response the coherence_bot will
        if not bucket:
            # if the bucket is empty generates a message for the user
            response = Response({
                'result': random.choice(no_response_templates),
                'bot_name': 'empty_bucket',
                'user_attributes': {},
                'bot_params': {},
                'lock_requested': False
            })
        else:
            logger.debug("---------------- Bucket -----------------------")
            logger.info('Bots in bucket: %s' % ', '.join([x.bot_name for x in bucket]))
            logger.debug("Bucket: \n{}".format(
                "\n".join(map(lambda x: "-- [{}]{}: {}".format(x.bot_name, "[L]" if x.lock_requested else "", x.result), bucket)))
            )

            # Filter bucket for profanity, length, etc.
            bucket = self.bucket_filter.filter(bucket, history, nlu_annotations)

            logger.info('Bots in filtered bucket: %s' % ', '.join([x.bot_name for x in bucket]))
            # logger.debug("Filtered bucket: \n{}".format(
            #     "\n".join(map(lambda x: "[{}]: {}".format(x.bot_name, x.result), bucket)))
            # )

            # Send populated bucket to the selection strategy module to pick a response
            response = self.ranker.select_response(bucket, self.state_manager.current_state, history)
            logger.debug("----------------------------------------------")

        # adding drivers if needed
        response.result, coherence_attributes, coherence_lock = self.postprocessor.fix_drivers(
            response.result,
            bucket
        )

        # Update state with info from selected bot
        self.state_manager.update_state_with_response(result=response.result,
                                                      bot_name=response.bot_name,
                                                      lock_requested=response.lock_requested,
                                                      bot_state=response.bot_params,
                                                      user_attr=response.user_attributes)
        # replacing user name in the response
        response.result = self.postprocessor.replace_username(
            response.result,
            response.user_attributes.get('user_name', self.state_manager.user_name)
        )

        ################### EMOTIONAL STUFF ###################
        # get the emotional output tag and shift if present
        # TODO: (IDEA) Proccess multiple tags in the same sentence
        response.result, tts_emotion, emotion_shift = self.postprocessor.emotion_postprocess(response.result)
        if tts_emotion:
            response.emotion = tts_emotion
            logger.debug("Response is said as: %s" % tts_emotion)

        if emotion_shift:
            self.emotional_model.adjust_emotion(emotion_shift)
            self.state_manager.system_emotion = self.emotional_model.check_state()
            logger.debug("Emotion shifted by: {}. System emotion is {}".format(emotion_shift, self.state_manager.system_emotion))


        # updating coherence attributes if a driver was added
        if coherence_attributes:
            self.state_manager.bot_states['coherence_bot'] = {
                'lock_requested': coherence_lock,
                'bot_attributes': coherence_attributes
            }
            # self.state_manager.current_state['state']['bot_states']['coherence_bot'] = coherence_attributes
            self.state_manager.set_response_edits({'driver_added': coherence_attributes.get('driver', '')})
        self.state_manager.save_current_state()

        # if requested, add NLU annotations + list of bots in bucket to the returned value
        if debug_info_requested:
            response.debug_info = self._prepare_debug_info(nlu_annotations, bucket)

        logger.info("Selected response: [{}]: {}".format(response.bot_name, response.result))
        # logger.debug(json.dumps(self.state_manager.current_state, indent=4))
        logger.debug(response.toJSON())
        return response.toJSON()

    def call_bots(self, state, history, user_attributes):
        """
        Populates the bucket with all the candidate responses. All bots the get the same information, which is:
        current_state: the state dictionary
        history: the n-th last turns
        user_attributes: the user attributes of the current speaking user
        :param state: the current state dictionary
        :param history_depth: the depth of the history to be forwarded
        """
        data = {
            'current_state': state,
            'history': history,
            'user_attributes': user_attributes
        }

        bucket = []

        with ThreadPoolExecutor(max_workers=len(self.config.BOT_LIST)) as executor:
            futures_annotations = {
                executor.submit(call_module, **{"url": bot_url,
                                                "module_name": bot_name,
                                                "data": data,
                                                "timeout": self.config.BOT_TIMEOUT}): bot_name
                for bot_name, bot_url in self.config.BOT_LIST.items()
            }

            for future in concurrent.futures.as_completed(futures_annotations):
                if future and future.result():
                    responses = [Response(br) for br in future.result() if br["result"]]
                    if responses:
                        bucket.extend(responses)

            return bucket

    def _prepare_debug_info(self, nlu_annotations, bucket):
        debug_info = dict(nlu_annotations['annotations']) if nlu_annotations else {}
        # simplifying entity linking printouts
        if 'entity_linking' in debug_info:
            debug_info["entity_linking"] = format_linker_info(debug_info["entity_linking"])
        if 'bot_entities' in debug_info:
            debug_info["bot_entities"] = format_linker_info(debug_info["bot_entities"])
        if 'user_preferences' in debug_info and 'entity' in debug_info['user_preferences']:
            debug_info['user_preferences']['entity'] = format_linker_info({'': debug_info['user_preferences']['entity']})['']
        # additional info
        debug_info['bucket'] = [resp.bot_name for resp in bucket] if bucket else 'EMPTY'
        debug_info['hub'] = {'version': VERSION, 'hostname': HOSTNAME}
        return debug_info


def cli(args):
    utils.log.set_logger_params('alana-' + BRANCH,
                                logfile=args.logfile,
                                file_level=args.file_verbosity,
                                console_level=args.console_verbosity)

    with open(args.config_file, 'r', encoding='UTF-8') as fh:
        config = DictQuery(yaml.load(fh))

    ranker = create_selection_strategy(config)
    postprocessor = Postprocessor(filter_attr=config.SENTENCE_FILTER)
    bucket_filter = BatchFilter(config.SENTENCE_FILTER)
    emotional_model = EmotionalModel()

    session_id = args.override_sessid if args.override_sessid else 'CLI-' + str(uuid.uuid4())
    user_id = args.userid

    alana_params = {
        "config": config,
        "ranker": ranker,
        "postprocessor": postprocessor,
        "bucket_filter": bucket_filter,
        "emotional_model": emotional_model
    }

    while True:
        try:
            text = input("> ")
            if text == "stop" or "":
                break
            alana = AlanaMain(**alana_params)
            result = (alana.get_answer(session_id=session_id, text=text, user_id=user_id))
            print("Alana: %s" % result.get('result'))
        except KeyboardInterrupt:
            break

    print("Completed conversation with session ID {}".format(session_id))


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        utils.log.set_logger_params('alana-' + BRANCH,
                                    logfile=self.options['logfile'],
                                    file_level=self.options['file_verbosity'],
                                    console_level=self.options['console_verbosity'])

        with open(self.options['config_file'], 'r', encoding='UTF-8') as fh:
            config = DictQuery(yaml.load(fh))

        ranker = create_selection_strategy(config)
        postprocessor = Postprocessor(filter_attr=config.SENTENCE_FILTER)
        bucket_filter = BatchFilter(config.SENTENCE_FILTER)
        emotional_model = EmotionalModel(logger=self.logger)

        api.add_resource(
            AlanaMain,
            "/",
            resource_class_kwargs={
                "config": config,
                "ranker": ranker,
                "postprocessor": postprocessor,
                "bucket_filter": bucket_filter,
                "emotional_model": emotional_model
            }
        )

        return self.application


if __name__ == '__main__':
    ap = ArgumentParser(description='Bot bucket')
    ap.add_argument('-c', '--config_file', type=str, help='Path to the config file (YAML)',
                    required=True)
    ap.add_argument('-s', '--server', action='store_true',
                    help='Run as a (multi-threaded) server.')
    ap.add_argument('-p', '--port', type=int, default=5000,
                    help='Port on which to run as a server (default: 5000)')
    ap.add_argument('-uid', '--userid', type=str, default='dummy-user')
    ap.add_argument('-cv', '--console-verbosity', default='info', help='Console logging verbosity')
    ap.add_argument('-fv', '--file-verbosity', default='debug', help='File logging verbosity')
    ap.add_argument('-l', '--logfile', default='logs/alana.log', help='Path to the log file')
    ap.add_argument('-w', '--workers', default=8, help='Number of workers')
    ap.add_argument('-d', '--debug', action='store_true', help='1 worker & 1hr timeout')
    ap.add_argument('--override-sessid',
                    help='Connect to a specific session ID and continue (console only, use with caution!)')

    args = ap.parse_args()

    if args.server:
        options = {
            'bind': '%s:%s' % ('0.0.0.0', args.port),
            'workers': args.workers,
            'port': args.port,
            'file_verbosity': args.file_verbosity,
            'logfile': args.logfile,
            'console_verbosity': args.console_verbosity,
            'server': args.server,
            'config_file': args.config_file
        }
        if args.debug:
            options['workers'] = 1
            options['timeout'] = 3600

        StandaloneApplication(app, options).run()
    else:
        cli(args)
