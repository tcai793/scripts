from telethon import TelegramClient, events, sync
import sys
import json
import os
import errno
from metadata import *


def save_one_message(message, chat_path, chatinfo):
    # Process chat metadata
    if chatinfo['min_processed_id'] > message.id:
        chatinfo['min_processed_id'] = message.id
    if chatinfo['max_processed_id'] < message.id:
        chatinfo['max_processed_id'] = message.id

    grouped_id = message.grouped_id

    if grouped_id is not None:
        # Album Message
        # Check if grouped_id exist, if so add file to that folder
        if grouped_id in chatinfo['album_mapping']:
            folder_id = chatinfo['album_mapping'][grouped_id]
            message_path = os.path.join(chat_path, str(folder_id))

            # Download media file
            create_dir_if_nonexist_from_dirname(message_path)
            message.download_media(file=message_path)

            # Append new id to messageinfo
            messageinfo = load_messageinfo(message_path)
            messageinfo['ids'].append(message.id)
            save_messageinfo(messageinfo, message_path)
        else:
            # If not, then create new folder
            folder_id = message.id
            message_path = os.path.join(chat_path, str(folder_id))
            chatinfo['album_mapping'][grouped_id] = folder_id

            # Download media file
            create_dir_if_nonexist_from_dirname(message_path)
            message.download_media(file=message_path)

            # Write messageinfo
            messageinfo = create_messageinfo(message)
            save_messageinfo(messageinfo, message_path)

    else:
        # Normal Message
        message_path = os.path.join(chat_path, str(message.id))
        messageinfo = create_messageinfo(message)

        # Download media
        create_dir_if_nonexist_from_dirname(message_path)
        message.download_media(file=message_path)

        # Write messageinfo
        save_messageinfo(messageinfo, message_path)


def save_range_messages(client, chat_id, chat_path, chatinfo, count, total, min_id=0, max_id=0):
    for message in client.iter_messages(chat_id, reverse=True, min_id=min_id, max_id=max_id):
        count += 1
        print('{}/{}'.format(count, total), end='\r')

        save_one_message(message, chat_path, chatinfo)

        # Save chat metadata
        save_json(chatinfo, os.path.join(chat_path, 'chatinfo.json'))

    return count


def save_all_messages(client, chat_id, chat_path):
    # Variable used to display progress
    total = client.get_messages(chat_id).total
    count = 0

    # Pre processing
    # Load dictionary
    chatinfo = load_chatinfo(chat_path)

    min_processed_id = dictionary_get_or_default(
        chatinfo, 'min_processed_id', 0)
    max_processed_id = dictionary_get_or_default(
        chatinfo, 'max_processed_id', 0)

    # Chat metadata
    if chatinfo == {}:
        chatinfo = create_chatinfo(client, chat_id)

    # Process all messages
    if min_processed_id is 0:
        # Nothing downloaded yet, start new download
        count = save_range_messages(
            client, chat_id, chat_path, chatinfo, count, total)
    else:
        # Resume previous download
        count = save_range_messages(client, chat_id, chat_path, chatinfo, count, total, max_id=min_processed_id)
        count = save_range_messages(client, chat_id, chat_path, chatinfo, count, total, min_id=max_processed_id)


def same_grouped_id_has_same_text(client, chat_id):
    dic = {}
    for message in client.iter_messages(chat_id, reverse=True):
        grouped_id = message.grouped_id
        if grouped_id is None:
            continue

        if grouped_id in dic:
            dic[grouped_id].append(message.raw_text)
        else:
            dic[grouped_id] = [message.raw_text]

    save_json(dic, './test.json')


if __name__ == '__main__':
    # Parse config
    config = {}
    with open('config.json') as config_fp:
        config = json.load(config_fp)

    api_id = config['api_id']
    api_hash = config['api_hash']
    chat_name = config['chat_name']
    root_folder = config['root_folder']
    session_name = config['session_name']

    # Setup client

    client = TelegramClient(session_name, api_id, api_hash)

    client.start()

    # Search chat
    chat_id = get_chat_id(client, chat_name)

    chat_path = os.path.join(root_folder, chat_name + '-' + str(chat_id))

    # Step 1: save all messages
    save_all_messages(client, chat_id, chat_path)

    #same_grouped_id_has_same_text(client, chat_id)
