from config import CONFIG
from module_interface import Module_Interface
from paper import Paper

import json
import logging
import builtins

import transmissionrpc


class Module_Transmission:
    def __init__(self, paper):
        self._paper = paper
        self._anything_printed = False

    def _parse_config(self):
        config_f = open(CONFIG.TRANSMISSION_CONFIG_PATH)
        self._config = json.load(config_f)
        config_f.close()

        if 'host' not in self._config:
            raise AttributeError("Key host not found in config file")
        if 'port' not in self._config:
            raise AttributeError("Key port not found in config file")
        if 'username' not in self._config:
            raise AttributeError("Key username not found in config file")
        if 'password' not in self._config:
            raise AttributeError("Key password not found in config file")

    def _check_paper(self):
        if self._anything_printed is False:
            self._paper.new_module("Transmission")
            self._anything_printed = True
        else:
            self._paper.add_text()

    def run(self):
        # Parse config
        self._parse_config()
        logging.info("Config parsed")

        host = self._config['host']
        port = self._config['port']
        username = self._config['username']
        password = self._config['password']

        old_db = {
            "completed": [
            ],
            "error": {
            },
            "accessble": True
        }

        new_db = {
            "completed": [
            ],
            "error": {
            },
            "accessble": True
        }

        try:
            db_f = open(CONFIG.TRANSMISSION_DB_PATH)
            old_db = json.load(db_f)
            db_f.close()
        except FileNotFoundError as e:
            pass

        tc = transmissionrpc.Client(
            address=host, port=port, user=username, password=password)

        torrents = tc.get_torrents()

        # Check accessble
        if tc.port_test() is False:
            new_db["accessble"] = False
            if old_db["accessble"] is True:
                self._check_paper()
                self._paper.add_text("Warning", bold=1)
                self._paper.add_text("Port unaccessble")
                self._paper.add_text()

        # Check error
        empty = True
        for t in torrents:
            seedhash = t.hashString

            if t.error is not 0:
                new_db["error"][seedhash] = t.errorString
                if seedhash not in old_db["error"].keys() or \
                        not old_db["error"][seedhash] == t.errorString:
                    continue
                    # Add to paper
                    self._check_paper()
                    if empty:
                        self._paper.add_text("Error", bold=1)
                        empty = False
                    else:
                        # Empty line between items
                        self._paper.add_text()

                    self._paper.add_text(
                        "{}:\n{}".format(t.name, t.errorString))

        # Check completed
        empty = True
        for t in torrents:
            seedhash = t.hashString

            if t.percentDone == 1:
                new_db["completed"].append(seedhash)
                if seedhash not in old_db["completed"]:
                    # Add to paper
                    self._check_paper()
                    if empty:
                        self._paper.add_text("Download Finished", bold=1)
                        empty = False
                    else:
                        # Empty line between items
                        self._paper.add_text()

                    self._paper.add_text(t.name)

        db_f = open(CONFIG.TRANSMISSION_DB_PATH, 'w')
        json.dump(new_db, db_f)
        db_f.close()
