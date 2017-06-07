# encoding: utf-8

"""

Acquire Veðurstofa Íslands stations from stafli and dump them to yaml together with the provider.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import argparse
from util.db_connection import WHConnection
from util.utilities import configure_logging, load_config, whLogger
from setup_stations import dump_provider_and_stations

LOG = whLogger(__name__)


def acquire_vedurstofan_stations(import_url):
    conn = WHConnection(import_url)
    sql = "select stod, nafn, skst, stod_wmo, h_stod, breidd_y, lengd_x, teg, endir from stod"
    sql += " where (teg='sj' and stod between 1000 and 6000) or (teg in ('vf', 'sk'))"
    with conn.trans() as wht:
        stafli_stations = wht.get_data(sql)
    LOG.info('Acquired %d stations from remote server', len(stafli_stations))
    stations = []
    for row in stafli_stations:
        stations.append({
            'ref': 'vi.is.' + row['skst'],
            'ref_provider': row['stod'],
            'name': row['nafn'],
            'ref_wmo': row['stod_wmo'],
            'lat': row['breidd_y'] * 10,
            'lon': row['lengd_x'] * -10,
            'has': (row['h_stod'] * 10 if row['h_stod'] is not None else None),
            'active': not row['endir'],
            'manual': row['teg'].strip() in ['vf', 'sk']
        })
    return stations


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='Config file for program. Required')
    return parser.parse_args()


def main():
    args = parse_args()
    configure_logging(os.path.join(os.path.dirname(__file__), 'logging.yml'))
    config = load_config(args.config)

    stations = acquire_vedurstofan_stations(config['db_url_source'])
    provider = {'name': 'Vedurstofan', 'ref': 'vi.is'}
    filename = os.path.join(os.path.dirname(__file__), 'setup_files/setup_vi_is.yml')

    dump_provider_and_stations(provider, stations, filename)


if __name__ == '__main__':
    main()
