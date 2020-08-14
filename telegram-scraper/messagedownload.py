from telethon import TelegramClient, events, sync
import sys
import json
import os
import errno
from metadata import *


def download_all_media_file(message, message_path):
    create_dir_if_nonexist_from_dirname(message_path)
    message.download_media(file=message_path)

    # If page is a webpage, download all photos and documents cached in page
    try:
        for photo in message.web_preview.cached_page.photos:
            message.client.download_media(photo, file=message_path)

        for doc in message.web_preview.cached_page.documents:
            message.client.download_media(doc, file=message_path)
    except Exception as exc:
        pass


def save_one_message(message, chat_path, chatinfo):
    # Process chat metadata
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
            download_all_media_file(message, message_path)

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
            download_all_media_file(message, message_path)

            # Write messageinfo
            messageinfo = create_messageinfo(message)
            save_messageinfo(messageinfo, message_path)

    else:
        # Normal Message
        message_path = os.path.join(chat_path, str(message.id))
        messageinfo = create_messageinfo(message)

        # Download media
        download_all_media_file(message, message_path)

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

    max_processed_id = dictionary_get_or_default(
        chatinfo, 'max_processed_id', 0)

    # Chat metadata
    if chatinfo == {}:
        chatinfo = create_chatinfo(client, chat_id)

    # Download all messages
    count = save_range_messages(client, chat_id, chat_path, chatinfo, count, total, min_id=max_processed_id)


def messagedownload(api_id, api_hash, chat_names, root_folder, session_name):

    # Setup client

    client = TelegramClient(session_name, api_id, api_hash)

    client.start()

    for counter, chat_name in enumerate(chat_names):
        print('Downloading chat: {} ({}/{})'.format(chat_name, counter+1, len(chat_names)))

        # Search chat
        chat_id = get_chat_id(client, chat_name)

        chat_path = os.path.join(root_folder, chat_name + '-' + str(chat_id))

        # Save all messages
        save_all_messages(client, chat_id, chat_path)
