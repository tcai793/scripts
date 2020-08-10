import logging
from memobird_agent import Document
import json
import builtins
import socket
from datetime import datetime
from croniter import croniter

from paper import Paper
from config import CONFIG
from module_list import module_list

from module_interface import Module_Interface


def parse_config(path_to_config):
    config = {}
    with open(path_to_config) as config_f:
        config = json.load(config_f)

    if not 'hostname' in config:
        config['hostname'] = socket.gethostname()

    if not 'modules' in config:
        raise AttributeError("When parsing main config: modules not found!")

    if not 'memobird_smart_guid' in config:
        raise AttributeError(
            "When parsing main config: memobird_smart_guid not found!")

    if not 'memobird_user_id' in config:
        raise AttributeError(
            "When parsing main config: memobird_user_id not found!")

    return config


if __name__ == '__main__':
    # Log current time for use by other modules
    builtins.now = datetime.now()

    # Open logging file
    logging.basicConfig(
        filename=CONFIG.LOG_FILE_PATH,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    logging.info(
        '----------------------------- Begin of this run -----------------------------')

    # Parse config
    try:
        config = parse_config(CONFIG.MAIN_CONFIG_PATH)
    except BaseException as exc:
        logging.error("Failed to parse MAIN CONFIG: {0}".format(exc))
        exit(-1)

    # Create paper
    paper = Paper(config['hostname'])
    logging.info("paper created")

    # Run each module if meet cron time requirement and enabled in config
    for mod in module_list:
        # Check if enabled
        if mod not in config['modules']:
            logging.info("----- Module {} is disabled -----".format(mod))
            continue

        # Check if meet cron time requiremnt
        try:
            cron_format = config['modules'][mod]
            if not croniter.match(cron_format, builtins.now):
                logging.info(
                    '----- Module {} runtime not reched. Next run at {} -----'.format(
                        mod,
                        croniter(cron_format, builtins.now).get_next(datetime)
                    )
                )
                continue

        except BaseException as exc:
            logging.warning('crontime set for this module cannot be parsed. "{}": {}'.format(
                config['modules'][mod], exc))

        logging.info("----- Begin {0} Module -----".format(mod))

        # Module is scheduled to run
        try:
            module_list[mod](paper).run()
        except AttributeError as exc:
            logging.error(
                "Error occurred when running module {0}: {1}".format(mod, exc))
        except BaseException as exc:
            logging.critical(
                "Critical Error occurred when running module {0}: {1}".format(mod, exc))

        logging.info("------ End {0} Module ------".format(mod))

    # Print documents
    # Only print documents that have content
    smart_guid = config['memobird_smart_guid']
    user_id = config['memobird_user_id']

    if paper.is_empty():
        logging.info("Document is empty, not printing")
    else:
        logging.info('Document print to machine')
        paper.print(smart_guid, user_id)

    logging.info(
        '------------------------------ End of this run ------------------------------')
