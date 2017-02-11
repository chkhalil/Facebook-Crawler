# coding=utf-8

import io
import logging
import os

# Try to import simplejson first
try:
    import simplejson as json
except ImportError:
    import json

# Create the logger
logger = logging.getLogger(__name__)
# Mute the logger of the Requests module
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# create console handler
ch = logging.StreamHandler()

# add ch to logger
logger.addHandler(ch)


def load_data_from_json_file(file_path):
    """
    Load data from JSON file
    :param file_path: the input file's path
    :return: a list of facebook pages' id, an None if an exception happens
    """
    # Logging
    logger.info('Loading data from file : {}'.format(file_path))
    try:
        with open(file_path) as input_file:
            try:
                # Loading the facebook pages ids
                data = json.loads(input_file.read())
                # Logging
                logger.info('Data successfully loaded from file : {}'.format(file_path))
            except Exception:
                # Empty dictionary if an error occurs
                data = None
                # Logging
                logger.exception('File {} not in JSON format'.format(file_path))
    except IOError:
        # Empty dictionary if an error occurs
        data = None
        # Logging
        logger.exception('Cannot load data from file : {}'.format(file_path))
    return data


def load_config_from_file(file_path):
    """
    Load the access token and the Graph API version to use from a config file
    :param file_path: the path of the configuration file
    :return: the access_token and the Graph API version
    """
    # Open the file where the authentication keys are stored
    config_data = load_data_from_json_file(file_path)
    if config_data is None:
        access_tokens = None
        graph_api_version = None
    else:
        # Get the list of access_tokens
        list_of_access_tokens = config_data['access_tokens']
        # Initialize a list of access_tokens
        access_tokens = []
        for access_token in list_of_access_tokens:
            # Creating the access token from the app_id and the app_secret values
            app_id = access_token['app_id']
            app_secret = access_token['app_secret']
            access_tokens.append("{}|{}".format(app_id, app_secret))
        # The Graph API version
        graph_api_version = config_data['graph_api_version']
    return access_tokens, graph_api_version


def create_new_file(file_path):
    """
    Create a file
    :param file_path: The full path of the file
    :return: IO Object
    """
    # Get filename
    file_name = file_path.split(os.sep)
    try:
        output_file = io.open(file_path, "a", encoding='utf8')
        # Logging
        logger.info('Successfully created file : {}'.format(output_file.name))
    except Exception:
        output_file = None
        # Logging
        logger.exception('Cannot create file : {}'.format(file_name))
    # Return statement
    return output_file


def export_json_data_to_file(json_data, file_path):
    """
    Export dictionary data to a file in JSON format
    :param json_data: Data to export
    :param file_path: Path of the JSON file where to save the data
    :return: Nothing
    """
    # Creating the file
    output_file = create_new_file(file_path)
    if output_file is None:
        # Logging
        logger.exception('Cannot export data to file : {}'.format(file_path))
    else:
        try:
            data = json.dumps(json_data, indent=2, ensure_ascii=False)
            output_file.write(unicode(data))
            output_file.flush()
            output_file.close()
            # Logging
            logger.info('Successfully exported data to file : {}'.format(file_path))
        except IOError:
            # Logging
            logger.exception('Cannot export data to file : {}'.format(file_path))


def create_directories(directories_path):
    """
    Check whether the path passed as argument exists, then create all the directories recursively
    :param directories_path: The path
    :return: Nothing
    """
    if os.path.exists(directories_path) is False:
        # Create the directories recursively
        os.makedirs(directories_path)
        # Logging
        logger.info('Directory : {} created successfully'.format(directories_path))
    else:
        # Logging
        logger.info('Directory : {} Already exists'.format(directories_path))


def get_directory_list(path, startswith=None, endswith=None, contains=None):
    """
    Returns the list of directories in the folder
    :param path: The folder path
    :param startswith: Start pattern
    :param endswith: End pattern
    :param contains: Contain pattern
    :return: List
    """
    # Initialize a new empty list
    list_dir = []
    # For each directory
    for d in os.listdir(path):
        # Initialize the boolean variables to include into the formula
        startswith_statement = True
        endswith_statement = True
        contains_statement = True
        # Check
        if startswith is not None:
            startswith_statement = d.startswith(startswith)
        if endswith is not None:
            endswith_statement = d.endswith(endswith)
        if contains is not None:
            contains_statement = d.__contains__(contains)
        # Check for the name of the directory if it matches the pattern
        if os.path.isdir(os.path.join(path, d)) and startswith_statement and endswith_statement and contains_statement:
            # Add it to the list
            list_dir.append(d)
    # Return
    return list_dir


def get_file_list(path, startswith=None, endswith=None, contains=None):
    """
    Return the list of files on that directory
    :param startswith: Start pattern
    :param endswith: End pattern
    :param contains: Contain pattern
    :param path: The path
    :return: list of file names in the path
    """
    # Initialize a new empty list
    list_files = []
    # For each directory
    for f in os.listdir(path):
        # Initialize the boolean variables to include into the formula
        startswith_statement = True
        endswith_statement = True
        contains_statement = True
        # Check
        if startswith is not None:
            startswith_statement = f.startswith(startswith)
        if endswith is not None:
            endswith_statement = f.endswith(endswith)
        if contains is not None:
            contains_statement = f.__contains__(contains)
        # Check for the name of the directory if it matches the pattern
        if os.path.isfile(os.path.join(path, f)) and startswith_statement and endswith_statement and contains_statement:
            # Add it to the list
            list_files.append(f)
    # Return
    return list_files
