# encoding: utf-8

"""

Read stations from Vegagerdin file and dump them to yaml together with the provider.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import codecs
import yaml
from util.utilities import configure_logging, whLogger
from setup_stations import dump_provider_and_stations

LOG = whLogger(__name__)


def read_vegagerdin_stations(filename=os.path.join(os.path.dirname(__file__), 'setup_files/setup_vegagerdin.yml')):

    """
    Read from yaml file with stations.
    Return list of dicts with stations, which will be ready for DB insert after adding provider id.
    """

    entries = []
    LOG.info("Reading Vegagerdin stations from file `%s`" % filename)
    with codecs.open(filename, encoding='utf-8') as yml_file:
        setup = yaml.safe_load(yml_file)
        for station in setup['points']:
            entry = {
                'ref': 'vg.is.%d' % station[0],
                'ref_provider': station[0],
                'name': station[5]['isl'],
                'ref_wmo': station[5].get('wmo', None),
                'lat': station[1],
                'lon': station[2],
                'has': station[3] if station[3] != '-' else None,
                #'hag': station[4]
            }

            entries.append(entry)
    return entries


def main():
    configure_logging(os.path.join(os.path.dirname(__file__), 'logging.yml'))

    provider = {'name': 'Vegagerdin', 'ref': 'vg.is'}
    stations = read_vegagerdin_stations()
    filename = os.path.join(os.path.dirname(__file__), 'setup_files/setup_vg_is.yml')

    dump_provider_and_stations(provider, stations, filename)

if __name__ == '__main__':
    main()
