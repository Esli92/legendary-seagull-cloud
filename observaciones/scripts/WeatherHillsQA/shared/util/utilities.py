# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import logging.config
import codecs
from datetime import timedelta, tzinfo

import yaml


def whLogger(name):
    """ Creates a logger within the weather-hills hierarchy for the module with the given name. """
    return logging.getLogger('wh.'+name)

LOG = whLogger(__name__)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)
utc = UTC()


def configure_logging(config_file_path):
    with open(config_file_path) as config:
        log_config = yaml.load(config)
    logging.config.dictConfig(log_config)
    LOG.info('Configured logging from %s', config_file_path)


def load_config(config_file_path):
    with codecs.open(config_file_path, encoding='utf-8') as yml_file:
        config = yaml.safe_load(yml_file)
    return config


def cut_error_msg(e):

    """
    Cut error message to 1000 characters. Use to print SQLAlchemy errors,
    as it tends to print whole error, which can be megabytes worth of chars long.
    """

    return str(e)[:1000] + (' (...)' if len(str(e)) > 1000 else '')


def make_regexp(ref):

    """ Convert format of station refs patterns to a proper regexp """

    if not ref.startswith('^'):
        ref = '^' + ref
    if not ref.endswith('$'):
        ref += '$'
    ref = ref.replace('.', '\.').replace('%', '.*')
    return ref
