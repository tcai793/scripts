import json
import os
from metadata import *
import re


def extract_hash_tag(chat_names, root_folder):
    counter = 1
    total = len(chat_names)

    for folder in os.listdir(root_folder):
        chat_path = os.path.join(root_folder, folder)

        # Check if this chat folder should be calculated
        chatinfo = load_chatinfo(chat_path)
        if chatinfo == {} or \
                chatinfo['chatname'] not in chat_names:
            continue

        for chat_id in os.listdir(chat_path):
            message_path = os.path.join(chat_path, chat_id)
            messageinfo = load_messageinfo(message_path)

            # Check if the message has a valid text
            if messageinfo == {} or \
                    messageinfo['raw_text'] is None or \
                    messageinfo['raw_text'] == '':
                continue

            hashtags = re.findall(r'#\w+', messageinfo['raw_text'])

            if len(hashtags) is 0:
                continue

            hashtags = {"hashtags": hashtags}

            save_hashtags(hashtags, message_path)
