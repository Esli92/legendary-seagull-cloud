#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
from sqlalchemy import create_engine
from util.db_tables import create_tables
from util.utilities import load_config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', required=True, help='Config file for program. Required')
    args = parser.parse_args()
    config = load_config(args.config)
    engine = create_engine(config['db_url'])
    create_tables(engine)
else:
    print('Why are you importing this file? That makes no sense!')
