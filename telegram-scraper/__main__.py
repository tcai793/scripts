from telethon import TelegramClient, events, sync
import sys
import json
import os
import errno


def get_chat_name(client, id):
    name = None
    for d in client.iter_dialogs():
        if d.id == id:
            return d.name

    print('Get chat name failed:{}'.format(id))
    sys.exit(-1)


def get_chat_id(client, chat_name):
    chat_id = -1
    for d in client.iter_dialogs():
        if d.name == chat_name:
            return d.id

    print('Get chat id failed:{}'.format(chat_name))
    sys.exit(-1)


def create_dir_if_nonexist_from_dirname(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def create_dir_if_nonexist_from_filename(filename):
    create_dir_if_nonexist_from_dirname(os.path.dirname(filename))


def save_json(obj, filename):
    create_dir_if_nonexist_from_filename(filename)
    with open(filename, 'w') as fp:
        json.dump(obj, fp, ensure_ascii=False)


def create_messageinfo(message):
    messageinfo = {}
    messageinfo['ids'] = [message.id]
    messageinfo['grouped_id'] = message.grouped_id
    messageinfo['date'] = message.date.strftime("%Y-%m-%d %H:%M:%S")
    messageinfo['out'] = message.out
    messageinfo['raw_text'] = message.raw_text
    messageinfo['action'] = type(
        message.action).__name__ if message.action else None

    return messageinfo


def create_chatinfo(client, chat_id):
    chatinfo = {}
    chatinfo['min_processed_id'] = -1
    chatinfo['max_processed_id'] = -1
    chatinfo['id'] = chat_id
    chatinfo['chatname'] = get_chat_name(client, chat_id)
    chatinfo['album_mapping'] = {}

    return chatinfo


def save_messageinfo(path, messageinfo):
    save_json(messageinfo, os.path.join(path, 'messageinfo.json'))


def save_all_messages_v2(client, chat_id, chat_path):
    total = client.get_messages(chat_id).total
    count = 0

    # Pre processing
    # TODO delete excessing folders

    # Chat metadata
    chatinfo = create_chatinfo(client, chat_id)
    # Message metadata
    downloadingAlbum = False
    last_grouped_id = -1
    message_path = None
    messageinfo = {}

    # Process all messages
    for message in client.iter_messages(chat_id, reverse=True, min_id=3806):
        count += 1
        print('{}/{}'.format(count, total), end='\r')

        # Process chat metadata
        if chatinfo['min_processed_id'] is -1:
            chatinfo['min_processed_id'] = message.id
        if chatinfo['max_processed_id'] < message.id:
            chatinfo['max_processed_id'] = message.id

        if downloadingAlbum:
            # In downloading album
            if message.grouped_id == last_grouped_id:
                # Maintain environment
                messageinfo['ids'].append(message.id)
                # Download media
                message.download_media(file=message_path)
                # Don't save metadata while downloading album to avoid partially
                # downloaded album
                continue
            else:
                # this album finished, save old messageinfo
                save_messageinfo(message_path, messageinfo)
                downloadingAlbum = False

        # download new content, may start new album
        last_grouped_id = message.grouped_id
        message_path = os.path.join(chat_path, str(message.id))
        create_dir_if_nonexist_from_dirname(message_path)
        messageinfo = create_messageinfo(message)
        # Download media
        message.download_media(file=message_path)

        if message.grouped_id is not None:
            # Start of album
            # Setup environment
            downloadingAlbum = True
        else:
            # Normal message
            save_messageinfo(message_path, messageinfo)

        # Save chat metadata
        save_json(chatinfo, os.path.join(chat_path, 'chatinfo.json'))

    if downloadingAlbum:
        save_messageinfo(message_path, messageinfo)


if __name__ == '__main__':
    # Parse config
    config = {}
    with open('config.json') as config_fp:
        config = json.load(fp)

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

    chat_path = os.path.join(root_folder=root_folder, chat_name + '-' + str(chat_id))

    # Step 1: save all messages
    save_all_messages_v2(client, chat_id, chat_path)
