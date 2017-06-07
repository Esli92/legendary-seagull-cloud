"""

Utilities for writing unit tests.

On startup we load project_path and test_config which are then used by other
utilities.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import sys
import requests
from util.db_connection import WHConnection
from util.utilities import load_config, whLogger

LOG = whLogger(__name__)


logging.basicConfig(level=logging.INFO)


def load_test_config():
    my_path = os.path.abspath(os.path.dirname(__file__))
    project_path = os.path.abspath(os.path.join(my_path, '..', '..', '..'))
    config_path = os.path.join(project_path, 'test_config.yml')
    if not os.path.isfile(config_path):
        print('PLEASE CREATE TEST CONFIG FILE ' + config_path)
        print('For example by copying and customizing ' + os.path.join(my_path, 'test_config_template.yml'))
        raise IOError('Test configuration file not found: ' + config_path)
    try:
        return project_path, load_config(config_path)
    except IOError:
        logging.exception('Failed to load test config from ' + config_path)
        raise


project_path, test_config = load_test_config()


def ensure_data(sub_path):
    """
    Returns a path to sub_path within WeatherHills/test_data, down-loading
    it from $test_data_source first if needed. """
    local_path = os.path.join(project_path, 'test_data', sub_path)
    local_dir = os.path.dirname(local_path)
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)
    if not os.path.isfile(local_path):
        url = os.path.join(test_config['test_data_source'], sub_path)
        LOG.info('Fetch %s', url)
        r = requests.get(url)
        r.raise_for_status()
        size = 0
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    size += len(chunk)
                    f.write(chunk)
        LOG.info('Downloaded %d.2 MB', size / 1024 / 1024)
    LOG.info('Ensured data: %s', local_path)
    return local_path


def make_WHConnection():
    db_url = test_config['db_url']
    return WHConnection(db_url)
