""" Setup the stations that LV operates, not related to wind turbines """

# encoding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import codecs
from util.utilities import configure_logging, whLogger
from setup_stations import dump_provider_and_stations

LOG = whLogger(__name__)


keys_map = {
    'STOD': ('ref_provider', str),
    'NAFN': ('name', unicode),
    'SKST': ('ref', lambda x: 'lv.is.' + x),
    'BREIDD_Y': ('lat', float),
    'LENGD_X': ('lon', float),
    'H_STOD': ('has', float)
}


def read_landsvirkjun_stations(filename, separator=',', nodata='-9999.0'):
    entries = []
    LOG.info("Reading Landsvirkjun stations from file `%s`" % filename)

    with codecs.open(filename, encoding='UTF-8') as lv_file:
        headers = lv_file.readline().strip().split(separator)
        keys = [keys_map[h] for h in headers]

        for line in lv_file:
            data = line.strip().split(separator)
            entry = {k[0]: k[1](v) for k, v in zip(keys, data) if v != nodata}
            entries.append(entry)

    return entries


def main():
    configure_logging(os.path.join(os.path.dirname(__file__), 'logging.yml'))

    provider = {'name': 'Landsvirkjun', 'ref': 'lv.is'}
    stations = read_landsvirkjun_stations(os.path.join(os.path.dirname(__file__), 'setup_files/lv_stations.txt'))
    filename = os.path.join(os.path.dirname(__file__), 'setup_files/setup_lv_is.yml')

    dump_provider_and_stations(provider, stations, filename)


if __name__ == '__main__':
    main()

