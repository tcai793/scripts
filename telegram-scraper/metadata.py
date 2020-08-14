import os
import json
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

# Folder related


def create_dir_if_nonexist_from_dirname(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def create_dir_if_nonexist_from_filename(filename):
    create_dir_if_nonexist_from_dirname(os.path.dirname(filename))

# Save metadata


def save_json(obj, filename):
    create_dir_if_nonexist_from_filename(filename)
    with open(filename, 'w') as fp:
        json.dump(obj, fp, ensure_ascii=False)


def save_hashtags(hashtags, path):
    save_json(hashtags, os.path.join(path, 'hashtags.json'))


def save_messageinfo(messageinfo, path):
    save_json(messageinfo, os.path.join(path, 'messageinfo.json'))


# Load metadata

def load_json(filename):
    try:
        with open(filename) as fp:
            metadata = json.load(fp)
            return metadata
    except Exception:
        return {}


def load_messageinfo(path):
    return load_json(os.path.join(path, 'messageinfo.json'))


def load_chatinfo(path):
    return load_json(os.path.join(path, 'chatinfo.json'))

# Create metadata


def create_messageinfo(message):
    messageinfo = {}
    messageinfo['ids'] = [message.id]
    messageinfo['grouped_id'] = message.grouped_id
    messageinfo['date'] = message.date.strftime("%Y-%m-%d %H:%M:%S")
    messageinfo['out'] = message.out
    messageinfo['raw_text'] = message.raw_text
    messageinfo['action'] = type(message.action).__name__ if message.action else None

    return messageinfo


def create_chatinfo(client, chat_id):
    chatinfo = {}
    chatinfo['max_processed_id'] = 0
    chatinfo['id'] = chat_id
    chatinfo['chatname'] = get_chat_name(client, chat_id)
    chatinfo['album_mapping'] = {}

    return chatinfo


def dictionary_get_or_default(dic, key, default):
    return dic[key] if key in dic else default
