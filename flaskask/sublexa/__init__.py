from flask import Flask, json
from flask_ask import Ask, question, statement, session, audio, current_stream, logger
import logging
import os
from pprint import pprint
from qmanager import QueueManager

log_level = logging.DEBUG
logging.getLogger("flask_ask").setLevel(log_level)

app = Flask(__name__)
ask = Ask(app, '/alexa')
    
from . import intents