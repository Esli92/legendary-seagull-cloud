# encoding: utf-8

"""

Read stations from Landsverk file and dump them to yaml together with the provider.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import codecs
from util.utilities import configure_logging, whLogger
from setup_stations import dump_provider_and_stations

LOG = whLogger(__name__)


def read_landsverk_stations(filename=os.path.join(os.path.dirname(__file__), 'setup_files/setup_landsverk.csv')):

    """
    Read from csv file with stations, in a format provided by Landsverk (Faroe Islands)
    Return list of dicts with stations, which will be ready for DB insert after adding provider id.
    """

    entries = []

    LOG.info("Reading Landsverk stations from file `%s`" % filename)
    with codecs.open(filename, encoding='UTF-8') as metadata_file:
        for line in metadata_file.readlines()[1:]:
            if line.startswith("F"):
                data = line.split(";")
                ref_provider = data[0]
                lat, lon = map(float, data[2].replace(",", ".").split())
                entry = {
                    "ref_provider": ref_provider,
                    "ref": "lv.fo.%s" % ref_provider[1:],
                    "name": data[1],
                    "has": float(data[3]),
                    "lat": lat,
                    "lon": lon
                }
                entries.append(entry)
    return entries


def main():
    configure_logging(os.path.join(os.path.dirname(__file__), 'logging.yml'))

    provider = {'name': 'Landsverk', 'ref': 'lv.fo'}
    stations = read_landsverk_stations()
    filename = os.path.join(os.path.dirname(__file__), 'setup_files/setup_lv_fo.yml')

    dump_provider_and_stations(provider, stations, filename)


if __name__ == '__main__':
    main()
