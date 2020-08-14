import json
from messagedownload import messagedownload

if __name__ == '__main__':
    # Parse config
    config = {}
    with open('config.json') as config_fp:
        config = json.load(config_fp)

    api_id = config['api_id']
    api_hash = config['api_hash']
    chat_names = config['chat_names']
    root_folder = config['root_folder']
    session_name = config['session_name']

    # Step 1 download message
    messagedownload(api_id, api_hash, chat_names, root_folder, session_name)
