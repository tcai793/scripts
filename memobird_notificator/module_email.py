import json
import re
from exchangelib import Credentials, Account, EWSTimeZone
import logging

from config import CONFIG
from module_interface import Module_Interface
from paper import Paper


class Module_Email(Module_Interface):
    def __init__(self, paper):
        self._paper = paper
        self._has_email = False

    def _parse_config(self):
        config_f = open(CONFIG.EMAIL_CONFIG_PATH)
        self._config = json.load(config_f)
        config_f.close()

        if 'email' not in self._config:
            raise AttributeError("Key email not found in config file")

        if 'password' not in self._config:
            raise AttributeError("Key password not found in config file")

        if 'folders' not in self._config:
            raise AttributeError("Key folders not found in config file")

        if not isinstance(self._config['folders'], list):
            raise AttributeError("Key folders is not a list")

        if not isinstance(self._config['folders'][0], str):
            raise AttributeError("Key folders is not a list of string")

    def add_email(self, sender_name, sender_email, datetime_received, subject, text_body, limit=100):

        if not self._has_email:
            self._paper.new_module("Email")
            self._has_email = True

        # Process text_body to replace link and image
        text_body = text_body.strip()
        text_body = re.sub(r'\[.+\]', '[image]', text_body)
        text_body = re.sub(r'\<.+\>', '<link>', text_body)

        # Process text_body to limit length
        if len(text_body) > limit:
            text_body = text_body[:limit]
            text_body += '\n\n      !!! Email Cropped !!!'

        # Process datetime_received to current timezone and specified format
        tz_local = EWSTimeZone.localzone()
        datetime_modified = datetime_received.astimezone(tz=tz_local)
        time_str = datetime_modified.strftime('%Y/%m/%d %H:%M:%S %Z')

        # Append content to document
        self._paper.add_text("From: " + sender_name, bold=1)
        self._paper.add_text(sender_email)
        self._paper.add_text("Date: " + time_str, bold=1)
        self._paper.add_text("Subject: ", bold=1)
        self._paper.add_text(subject)
        self._paper.add_text()  # empty line
        self._paper.add_text(text_body)
        self._paper.add_sticker(42)

    def run(self):
        # Parse config
        self._parse_config()
        logging.info("Config parsed")

        # Set timezone

        # Process email
        email = self._config['email']
        password = self._config['password']

        # Open Account
        credentials = Credentials(email, password)
        account = Account(email, credentials=credentials, autodiscover=True)
        logging.info("Account opened")

        # Set folder
        folder = account.root
        for node in self._config['folders']:
            folder = folder / node
        logging.info("Folder changed")

        # Process inbox
        counter = 0
        for item in folder.all().order_by('-datetime_received'):
            # if the document is read then don't print it
            if item.is_read:
                continue

            counter += 1

            if counter > 20:
                break

            # Print the email
            self.add_email(item.sender.name, item.sender.email_address,
                           item.datetime_received, item.subject, item.text_body)
            logging.info("Email added")

            # Set the email to read
            item.is_read = True
            item.save(update_fields=['is_read'])

        if not self._has_email:
            logging.info("No new email")
