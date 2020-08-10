from config import CONFIG
from paper import Paper

import json
import logging
import builtins


class Module_Interface:
    def __init__(self, paper):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
