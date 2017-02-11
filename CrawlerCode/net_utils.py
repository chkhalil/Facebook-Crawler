# coding=utf-8

from __future__ import print_function

import logging
import sys
import time

import requests

import url_factory
# Create the logger
logger = logging.getLogger(__name__)


def make_request(url, param_dict=None):
    """
    Send a request using the URL and retrieve response
    :param url: The URL
    :param param_dict: The parameters used with the URL
    :return: None if the response is none and a dictionary else
    """
    # Logging
    if param_dict is None:
        logger.info('Sending request : {}'.format(url))
    else:
        p = ''
        is_it_the_first_param = True
        for key, value in param_dict.items():
            if is_it_the_first_param is True:
                p += '?{}={}'.format(key, value)
                is_it_the_first_param = False
            else:
                p += '&{}={}'.format(key, value)
        logger.info('Sending request : {}'.format(url + p))
    # Initialize a request counter and the response to None
    response = None
    requests_number = 0
    # Retries to make a request three times:
    while requests_number < 3:
        # Send request and retrieve response
        response = requests.get(url, param_dict)
        #response = requests.get(url)
        # Get the status code from response
        status_code = response.status_code
        # Compare with the HTTP code 200 : which is OK
        if status_code != 200:
            # Check if the code is 429
            if status_code == 429 or status_code == 403:
                # Too many requests or request forbidden
                time_to_sleep = 3600  # One hour
                # Increment the requests counter
                requests_number += 1
            else:
                # Temporary problems related to Facebook servers
                time_to_sleep = 60  # One minute
                # Increment the requests counter
                requests_number += 1
        else:
            break
        # Logging
        logger.info('Status code is {}'.format(status_code))
        logger.info('Retrying request in {} seconds'.format(time_to_sleep))
        # Sleep
        time.sleep(time_to_sleep)
    # If the number of requests is equal to three
    if requests_number == 3:
        logger.error('Cannot connect to the server !!')
    # Return statement
    return None if response is None else response.json()


def data_request(type_of, identifier, access_token, **kwargs):
    """
    Send a request to the Facebook servers and return a list containing all the posts of the page
    :param type_of: Type of the data to get
    :param access_token: The access token used to authenticate to the server
    :param identifier: The id to use to get the data
    :param since: The date from where to begin the crawl
    :param until: The date of the latest post
    :param number: The number of latest posts
    :return: List
    """
    # Create a Url object
    url = url_factory.Url()
    # Create the url to gather all the data depending on the type_of value
    _url = url.create_url(type_of, identifier, access_token, **kwargs)
    # Send a request and retrieve response
    data = make_request(_url.url, _url.param_dict)
    if data is None and (type_of == 'post' or type_of == 'page'):
        logger.error('There is no data ! please verify the request !')
        print('An error occurred, please check log file {}.log !!!'.format(identifier))
        sys.exit(-5)
    # If we're getting page info => no need to go to the next step
    if type_of == 'page':
        return data
    else:
        # Creating an empty list where to store the data
        storage_list = []
        # Collect all data requested
        storage_list = data_processing(data, storage_list, access_token, number=kwargs.get('number', None))[1]
        # Return statement
        return storage_list


def data_processing(data, storage_list, access_token, **kwargs):
    """
    Extract all the posts recursively
    :param storage_list: List where to store the posts
    :param data: the json dictionary containing the posts data
    :param access_token: The access token used to authenticate with to the server
    :param number: The number of latest posts
    :return:
    """
    # Get number argument from kwargs
    number = kwargs.get('number', None)
    # Extracting the paging data containing the next url
    try:
        paging = data['paging']
    except Exception:
        paging = None
    # Extract the data to process
    data_to_process = data['data']
    # For each entry
    for d in data_to_process:
        # Add the entry to the list
        storage_list.append(d)
        # If the user requested a number
        if number is not None:
            # Check if we got the number requested
            if len(storage_list) == number:
                # Return False to escape the while loop (recursion) and storage_list as the final list of data
                return False, storage_list
    # Check for next items
    if (paging is not None) and ('next' in paging):
        # Get the next url
        next_url = paging['next']
        while True:
            try:
                # Get the next data' page content
                more_data = make_request(next_url)
                # Extract data and return if there is a next entry in the paging field
                is_there_next, storage_list = data_processing(more_data, storage_list, access_token, **kwargs)
                # If there is no more data quit the loop
                if is_there_next is False:
                    break
            # If there is an exception, quit the loop
            except Exception:
                break
    # Return False to escape the while loop (recursion) and storage_list as the final list of data
    return False, storage_list
