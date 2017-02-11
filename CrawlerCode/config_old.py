# coding=utf-8

from __future__ import print_function

import os
import sys

import os_utils

# Useful directories
_working_dir = os.getcwd()
config_dir = os.path.join(_working_dir, 'config')
input_dir = os.path.join(_working_dir, 'input')
logs_dir = os.path.join(_working_dir, 'logs')
data_dir = os.path.join(_working_dir, 'data')
excel_dir = os.path.join(_working_dir, 'excel')
# Useful files
_config_file = os.path.join(config_dir, 'config.json')
_page_fields_file = os.path.join(config_dir, 'page_fields.json')
_posts_fields_file = os.path.join(config_dir, 'post_fields.json')
# Useful objects
page_fields = os_utils.load_data_from_json_file(_page_fields_file)
posts_fields = os_utils.load_data_from_json_file(_posts_fields_file)
# Application's access token and Facebook Graph API version to use
access_tokens, _graph_api_version = os_utils.load_config_from_file(_config_file)
if _graph_api_version is None:
    print("Couldn't load the Graph API version to use from config file !")
    sys.exit(1)
if access_tokens is None:
    print("Couldn't load the access token from config file !")
    sys.exit(2)
# Base url used to interact with the Graph API
graph_url = 'https://graph.facebook.com/v{}/'.format(_graph_api_version)
