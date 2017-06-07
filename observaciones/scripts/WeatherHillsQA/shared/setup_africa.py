""" Setup the stations for Africa got from https://madis-data.ncep.noaa.gov/public/sfcdumpguest.html """

# encoding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import codecs
import argparse
from util.utilities import configure_logging, whLogger
from setup_stations import dump_provider_and_stations

LOG = whLogger(__name__)


provider_refs = {
    'OTHER-MTR': 'af.mtr',
    'APRSWXNET': 'af.cwop',
    'MARITIME': 'af.mar'
}


def read_madis_file(filename, separator=','):
    entries = {}
    LOG.info("Reading Africa stations from file `%s`" % filename)

    with codecs.open(filename, encoding='UTF-8') as infile:
        for line in infile:
            if line.strip() == '':
                continue
            data = line.strip().split(separator)
            data = map(lambda s: s.strip(), data)
            if data[0] in entries:
                continue
            provider_ref = provider_refs[data[3]]
            entry = {
                'ref_provider': data[0],
                'name': data[0],
                'lon': float(data[13]),
                'lat': float(data[12]),
                'has': float(data[11]),
            }
            entry['ref'] = '{}.{}'.format(provider_ref, entry['ref_provider'].lower())
            entries[entry['ref_provider']] = (provider_ref, entry)

    entries2 = {k: [] for k in provider_refs.values()}

    for (provider_ref, e) in entries.values():
        entries2[provider_ref].append(e)

    return entries2


def main_multiple_files(files, collate=False):
    if collate:
        all_data = {k: [] for k in provider_refs.values()}

    for f in files:
        print ('Processing {}'.format(f))
        dirname, fname = os.path.split(f)
        outpath = os.path.join(dirname, 'output', 'setup_' + fname.replace('.txt', '{}_new.yml').replace('.csv', '{}.yml'))
        prov_and_stations = read_madis_file(f)
        for k, v in provider_refs.iteritems():
            provider = {'name': k, 'ref': v}
            if collate:
                all_data[v].extend(prov_and_stations[v])
            else:
                dump_provider_and_stations(provider, prov_and_stations[v], outpath.format(v))

    if collate:
        for k, v in provider_refs.iteritems():
            no_duplicates = {}
            for d in all_data[v]:
                no_duplicates[d['ref']] = d
            outpath = os.path.join(os.path.dirname(__file__), 'setup_files/setup_africa_{}.yml')
            provider = {'name': k, 'ref': v}
            dump_provider_and_stations(provider, no_duplicates.values(), outpath.format(v))


def main():
    configure_logging(os.path.join(os.path.dirname(__file__), 'logging.yml'))

    prov_and_stations = read_madis_file(os.path.join(os.path.dirname(__file__), 'setup_files/madis_ex2.csv'))
    filename_template = os.path.join(os.path.dirname(__file__), 'setup_files/setup_africa_{}2.yml')

    for k, v in provider_refs.iteritems():
        provider = {'name': k, 'ref': v}
        dump_provider_and_stations(provider, prov_and_stations[v], filename_template.format(v))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    parser.add_argument('--collate', action='store_true', default=False,
                        help="Use this if you want your setup files be collated and stored in default location")
    return parser.parse_args()


if __name__ == '__main__':
    # main()
    args = parse_args()
    main_multiple_files(args.files, args.collate)
