# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import codecs
import yaml

from util.utilities import whLogger

LOG = whLogger(__name__)
LANG_FILES = os.path.join(os.path.dirname(__file__), '../lang_data')


def load_yaml(path):
    try:
        with codecs.open(path, encoding='utf-8') as yml_file:
            data = yaml.safe_load(yml_file)
        return data

    except (IOError, KeyError, ValueError, yaml.scanner.ScannerError) as exc:
        LOG.error('Problem with reading from file. Does the file exist? Is it in the correct format?')
        LOG.exception(exc)
        raise


def load_dictionary(conf):
    path = conf.get('dictionary', os.path.join(LANG_FILES, 'dictionary_EN-{}.yml'.format(conf.get('lang', 'IS'))))
    LOG.info('Reading dictionary to translate the output from `%s`.', path)

    return load_yaml(path)


def possibly_load_char_map(conf):
    if 'ascii' not in conf or not conf['ascii']:
        return None

    path = os.path.join(LANG_FILES, conf.get('ascii_char_map', 'char_map_IS.yml'))
    LOG.info('UTF to ASCII character map will be loaded from `%s`.', path)

    return load_yaml(path)


def map_chars(text, char_map):
    if char_map is None:
        return text
    for non_asc, asc in char_map.iteritems():
        text = text.replace(non_asc, asc)

    try:
        text.decode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
        LOG.warning('Not all non-ascii characters have been removed from the string `%s`. Is your character map complete?', text)
    return text