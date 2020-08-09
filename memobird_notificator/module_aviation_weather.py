from config import CONFIG
from module_exception import ModuleException
from module_interface import Module_Interface
from paper import Paper

import json
import logging
import builtins

import requests
import re


class Module_Aviation_Weather(Module_Interface):
    def __init__(self, paper):
        self._paper = paper

    def _parse_config(self):
        config_f = open(CONFIG.AVIATION_WEATHER_CONFIG_PATH)
        self._config = json.load(config_f)
        config_f.close()

        if 'location' not in self._config:
            raise ModuleException("Key location not found in config file")

    def run(self):
        # Parse config
        self._parse_config()
        logging.info("Config parsed")

        location = self._config['location']

        # Get data
        response = requests.get(
            'https://aviationweather.gov/metar/data?ids={}&taf=on&layout=off'.format(location)).text

        match = re.findall(r'(?<=<code>)(.+)(?=<\/code>)', response)

        logging.info("Response from server received")

        if match:
            self._paper.new_module("Aviation Weather ")

            for i, line in enumerate(match):
                if i is 0:
                    self._paper.add_text("METAR:", bold=1)
                    self._paper.add_text(builtins.utctimestamp)
                if i is 1:
                    self._paper.add_text("TAF:", bold=1)

                line = re.sub("<br/>&nbsp;&nbsp;", "\n\n", line)
                self._paper.add_text(line)
                self._paper.add_text()
