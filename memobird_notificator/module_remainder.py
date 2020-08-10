from config import CONFIG
from module_interface import Module_Interface
from paper import Paper
from datetime import datetime
from croniter import croniter

import json
import logging
import builtins


class Module_Remainder(Module_Interface):
    def __init__(self, paper):
        self._paper = paper
        self._empty = True

    def _parse_config(self):
        config_f = open(CONFIG.REMINDER_CONFIG_PATH)
        self._config = json.load(config_f)
        config_f.close()

    def _add_content(self, text):
        if self._empty:
            self._paper.new_module("Reminder")
            self._empty = False
        else:
            # Add empty line between lines
            self._paper.add_text()

        self._paper.add_text(text)

    def _parse_time(self, timestr):
        time = datetime.strptime(timestr, '%Y%m%d%H%M')
        return time

    def _check_time(self, timestr):
        now = builtins.now

        time = self._parse_time(timestr)
        curr = datetime(now.year, now.month, now.day, now.hour, now.minute)

        return time == curr

    def _check_repeated_event(self, config):
        now = builtins.now

        if not config['enabled']:
            return

        if self._parse_time(config['start_datetime']) > now:
            return

        if now > self._parse_time(config['end_datetime']):
            return

        if croniter.match(config['event_crontime'], now):
            self._add_content(config['notification_text'])

    def _check_single_event(self, config):
        if not config['enabled']:
            return

        if self._check_time(config['event_datetime']):
            self._add_content(config['notification_text'])

    def run(self):
        # Parse config
        self._parse_config()
        logging.info("Config parsed")

        # Check repeated events
        for event in self._config["repeated_events"]:
            self._check_repeated_event(event)

        # Check single events
        for event in self._config["single_events"]:
            self._check_single_event(event)
