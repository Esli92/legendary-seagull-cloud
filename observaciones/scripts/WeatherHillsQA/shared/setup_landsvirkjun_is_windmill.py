# encoding: utf-8

"""

Create stations entries for Landsvirkjun and dump them to yaml together with the provider.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
from util.utilities import configure_logging, whLogger
from setup_stations import dump_provider_and_stations

LOG = whLogger(__name__)


def read_landsvirkjun_stations():
    entries = []
    LOG.info("Preparing entries for Landsvirkjun stations")

    for height in [2, 10, 31, 56, 57]:
        entries.append({
            "ref": "lv.ma.1.%02d" % height,
            "name": "Hafið mastur-1 %dm" % height,
            "ref_provider": "%02dm" % height,
            "lat": 64.1253334247,
            "lon": -19.7306082705,
            "hag": height,
            "has": 257.52
        })
    for windmill_nr in [1, 2]:
        entries.append({
            "ref": "lv.is.mi.%03d" % windmill_nr,
            "name": "Hafið mylla %d" % windmill_nr,
            "ref_provider": "mylla%d" % windmill_nr,
            "lat": 64.1253334247,
            "lon": -19.7306082705,
            "hag": 55,
            "has": 257.52
        })

    return entries


def main():
    configure_logging(os.path.join(os.path.dirname(__file__), 'logging.yml'))

    provider = {'name': 'Landsvirkjun', 'ref': 'lv.is'}
    stations = read_landsvirkjun_stations()
    filename = os.path.join(os.path.dirname(__file__), 'setup_files/setup_lv_is_windmill.yml')

    dump_provider_and_stations(provider, stations, filename)


if __name__ == "__main__":
    main()
