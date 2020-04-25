import logging
from memobird_agent import Document
import json

from module_exception import ModuleException
from module_interface import Module_Interface
from module_email import Module_Email
from paper import Paper
from config import CONFIG


def parse_config(path_to_config):
    config_f = open(path_to_config)
    config = json.load(config_f)
    config_f.close()

    if not 'hostname' in config:
        raise Exception("When parsing main config: log_file_path not found!")

    if not 'modules' in config:
        raise Exception("When parsing main config: modules not found!")

    if not 'memobird_smart_guid' in config:
        raise Exception(
            "When parsing main config: memobird_smart_guid not found!")

    if not 'memobird_user_id' in config:
        raise Exception(
            "When parsing main config: memobird_user_id not found!")

    return config


if __name__ == '__main__':
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
    paper = Paper()
    logging.info("paper created")

    # Run modules
    try:
        module_list = {
            "Email": Module_Email(paper),
            # "Reminder" : Module_Interface(),
            # "COVID" : Module_Interface()
        }
    except BaseException as exc:
        logging.critical(
            "Error occurred when creating module_list: {0}".format(exc))
        exit(-1)

    for mod in module_list:
        if mod in config['modules']:
            logging.info("----- Begin {0} Module -----".format(mod))
            try:
                module_list[mod].run()
            except ModuleException as exc:
                logging.error(
                    "Error occurred when running module {0}: {1}".format(mod, exc))
            except BaseException as exc:
                logging.critical(
                    "Critical Error occurred when running module {0}: {1}".format(mod, exc))
            finally:
                logging.info("------ End {0} Module ------".format(mod))
        else:
            logging.info("{0} module is not configured to run".format(mod))

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
