# coding=utf-8

from __future__ import print_function

import argparse
import datetime
import logging
import multiprocessing
import os
import random
import sys

import config
import model
import os_utils

def logger_config(page_id):
    """
    Logger configuration
    :param page_id: The page id
    :return: Nothing
    """
    # Configure the logging module
    logging.basicConfig(
        format='[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        filename=os.path.join(config.logs_dir, page_id),
        level=logging.DEBUG
    )
    # Return the logger
    return logging.getLogger(__name__)


def date_range(start, end, intv):
    """
    :param start: start crawl date
    :param end: end crawl date
    :param intv: number of periods to process
    :return:
    """
    from datetime import datetime, timedelta
    start = datetime.strptime(start,"%Y-%m-%d")
    end = datetime.strptime(end,"%Y-%m-%d")
    diff = (end  - start ) / intv
    for i in range(intv):
        date = (start + diff * i)
        yield date.strftime("%Y-%m-%d")
        if i!=0:
            date_plus = date + timedelta(days=1)
            yield date_plus.strftime("%Y-%m-%d")

    yield end.strftime("%Y-%m-%d")
    # return list of tuples: (strt-date, end_date)




def get_args_from_cli():
    """
    Get the arguments from the Command Line Interface
    :return:
    """
    # The script purpose
    parser = argparse.ArgumentParser(description='Launch a crawler on facebook using the input data')
    # Add the first optional argument for file input
    action_0 = parser.add_argument('-f', '--file', action='store_true', help='Use input file containing page ids')
    # Add the second optional argument to indicate the oldest's post date
    action_1 = parser.add_argument('-s', '--since', type=str,
                                   help='Oldest\'s post date in format AAAA-MM-DD')
    # Add a third optional argument to indicate the latest's post date
    action_2 = parser.add_argument('-u', '--until', type=str,
                                   help='Latest\'s post date in format AAAA-MM-DD (Can only be used when -s or --since'
                                        ' is used)')
    # Add a fourth optional argument to indicate the latest's post date
    action_3 = parser.add_argument('-e', '--excel', type=str,
                                   help='Generate Excel file containing stats with the name EXCEL (without extension)'
                                        ' : Can only be used when -f or --file is used')
    # Add a fifth optional argument to indicate the number of latest posts to get
    parser.add_argument('-n', '--number', type=int,
                        help='Number of latest posts to crawl (must be greater than 0)')

    # Add a sixth argument to mention dates breaking
    parser.add_argument('-b', '--daterange', type=bool,
                        help='True or False if we break date (default 4 if true)')

    # The input
    parser.add_argument('input', type=str, help='The input (By default, it\'s a page id if -f or --file is not used)')
    # Parse the arguments
    _args = parser.parse_args()
    # Get all the _args in a set
    argv = set(sys.argv)
    # Check if the until argument is used without the since argument (doing a set intersection)
    if (argv & set(action_2.option_strings)) and not (argv & set(action_1.option_strings)):
        # Display a parser error message
        parser.error('{} can only be used when {} is used'.format(' or '.join(action_2.option_strings),
                                                                  ' or '.join(action_1.option_strings)))
    # Check if the excel argument is used without the file argument (doing a set intersection)
    if (argv & set(action_3.option_strings)) and not (argv & set(action_0.option_strings)):
        # Display a parser error message
        parser.error('{} can only be used when {} is used'.format(' or '.join(action_3.option_strings),
                                                                  ' or '.join(action_0.option_strings)))
    # If the file flag is triggered
    if _args.file is True:
        # Check if the file exists
        if os.path.exists(_args.input) is False:
            print('Cannot find the file : {}\nPlease check the input path !'.format(_args.path))
            # Exit with code : -1
            sys.exit(-1)
    # Check if the number given is not under 0
    if _args.number is not None and _args.number <= 0:
        # Display a parser error message
        print('The number of posts to crawl must be greater than zero')
        # Exit with code : -2
        sys.exit(-2)
    # Return statement
    return _args



def main(page_id, user_path, access_token, launch_time_date, since, until, number):
    """
    Main program entry
    :param page_id: The id of the page to crawl
    :param user_path: The path where to store the data
    :param access_token: The access token used to authenticate to the server
    :param launch_time_date: The launch date and time
    :param since: The date from where to begin the crawl
    :param until: The date of the latest post
    :param number: The number of latest posts
    :return:
    """
    # Create the log's file name using today's date
    log_file_name = '{}-{}-{}-{}.{}'.format(page_id, launch_time_date, since, until, 'log')
    # Configure the logger
    logger = logger_config(log_file_name)
    # To avoid any exception
    try:
        # Create an object Page
        page = model.Page()
        # Get page information
        page.get_page_info(page_id, access_token)
        # Move to the posts
        page.get_posts(access_token, since=since, until=until, number=number, with_comments=True, with_replies=True,
                       with_reactions=True)
        # Get stats about the page
        page.get_stats()
        # The directory where to save the files
        write_directory = os.path.join(config.data_dir, user_path,
                                       '{}_-_{}_-_{}_-_{}'.format(getattr(page, 'name').encode('utf-8'), page_id, since, until))
        # Create the write directory if it doesn't exist
        os_utils.create_directories(write_directory)
        # Create the file name using today's date
        filename = '{}.{}'.format(launch_time_date, 'json')
        # Logging
        logger.info('Writing all the data to file {}'.format(filename))
        # Writing page info data to file
        os_utils.export_json_data_to_file(page.to_json(), os.path.join(write_directory, filename))
        print('All the information extracted from {} page !'.format(page_id))
    except Exception:
        print('An error occurred, please check the log file {}'.format(page_id))
        # Exit with status code : -4
        sys.exit(-4)


if __name__ == '__main__':
    # Get all arguments from the CLI
    args = get_args_from_cli()
    # Get the since, until and the number of posts values from cli
    since_value = args.since
    until_value = args.until
    until_value = args.until
    number_latest_posts = args.number
    break_date = args.daterange
    # Before starting, be sure that the directories are present in the current directory
    for _dir in [config.data_dir, config.excel_dir, config.logs_dir]:
        os_utils.create_directories(_dir)
    # Retrieve right now's date
    now = datetime.datetime.now()
    # Pattern
    launch_date_time = '{0}-{1}-{2}-{3}_{4}_{5}+{6}'.format(str(now.year), str(now.month), str(now.day), str(now.hour),
                                                            str(now.minute), str(now.second), str(now.microsecond))
    # Set the default write directory to the data dir
    write_path = config.data_dir
    # If the file flag is triggered
    if args.file is True:
        # List of processes
        jobs = []
        # list of inputs containing tuples (write_path, page_id)
        input_list = []
        # Represents the number of input data
        input_count = 0
        # Reading the file line by line and process it
        with open(args.input) as _file:
            # Read the first line
            line = _file.readline().replace('\n', '')
            while line != '':
                # If the line is all digits => the string is a page id
                if line.isdigit() is True:
                    # Append the actual tuple to the list of input data
                    input_list.append((line, write_path))
                    # Increment the input count by one
                    input_count += 1
                # Else => it's a path
                else:
                    # Update the write_path
                    write_path = line
                # Move on to the next line
                line = _file.readline().replace('\n', '')
        # Check if there is at least one page id
        if len(input_list) == 0:
            print('No page_id found\nPlease check your input file')
            # Exit with status code : -6
            sys.exit(-3)
        # separate date into list
        dates_list = list(date_range(since_value, until_value, 4))
        # create list of date tuples
        dates_tuple = [(dates_list[i], dates_list[i + 1]) for i in range(0, len(dates_list), 2)]

        # Get the number of available access_tokens
        number_of_access_tokens_available = len(config.access_tokens)
        # Prepare the processes to be started
        for input_tuple in input_list:
            # Create a new process for each input data and it to the list of jobs

            if break_date == True:
                # launch process for each date intervall

                for dates in dates_tuple:

                    jobs.append(multiprocessing.Process(target=main, args=input_tuple.__add__(
                        (config.access_tokens[input_list.index(input_tuple) % number_of_access_tokens_available],
                         launch_date_time, dates[0], dates[1], number_latest_posts))))
                    #main(input_list[0][0], input_list[0][1], config.access_tokens[input_list.index(input_tuple)], launch_date_time, dates[0], dates[1], number_latest_posts)



            else:
                    jobs.append(multiprocessing.Process(target=main, args=input_tuple.__add__(
                        (config.access_tokens[input_list.index(input_tuple) % number_of_access_tokens_available],
                         launch_date_time, since_value, until_value, number_latest_posts))))
            # Start the processes
            for j in jobs:
                j.start()
            # Ensure all of the processes have finished
            for j in jobs:
                j.join()
    else:
        # Start the crawling of the page
        main(args.input, write_path, config.access_tokens[random.randint(0, len(config.access_tokens) - 1)],
             launch_date_time, since_value, until_value, number_latest_posts)
    print('Program complete !')
