#!/usr/bin/env python
# encoding: utf-8

"""

Imports one or more files containing weather observations from the command-line.

"""

from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import os
import codecs
from collections import OrderedDict
from parser import find_parser
from util.db_connection import StationFinder, WHConnection
from util.utilities import configure_logging, load_config, whLogger
from util.data_sanity import check_data_sanity

LOG = whLogger(__name__)


def parse_args(argv_params=None):

    """
    :param argv_params: Pass a list in to parse that data instead of the process arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='Config file for program. Required')
    parser.add_argument('--parser', type=lambda p: find_parser(p, onerror=parser.exit), help='Name of ObservationParser to use')
    parser.add_argument('files', type=str, nargs='+', help='One or more files to import.')
    parser.add_argument('--log-config', default=os.path.join(os.path.dirname(__file__), 'logging.yml'),
                        help='Config file for logging. Defaults to logging.yml in code folder.')
    parser.add_argument('--sanity-null-replace', '-n', action='store_true', default=False,
                        help='If given, every data item falling behind their range will be silently replaced with null')
    parser.add_argument('--collate', '-c', action='store_true', default=False)
    parser.add_argument('--table', help='Target table', default='observation')
    parser.add_argument('--encoding', help='Add proper encoding name if the import fails on UTF-8', default='utf-8')
    parser.add_argument('--ignore-broken-lines', action='store_true', help='Omit non-parsable lines instead of rising exception')
    return parser.parse_args(argv_params)


def add_station_id(entries_set, metadata, station_finder):

    """ Update each entry in observation list with station id. """

    provider_ref = metadata.get('provider_ref', None)
    ref_provider = metadata.get('station_ref', None)
    if ref_provider:
        pk = station_finder.get_station_id(ref_provider=ref_provider, provider_ref=provider_ref)
        for entry in entries_set:
            entry['station_id'] = pk
    else:  # so the station_ref should be inside each entry
        new_entries_set = []
        refs_to_ids = {}
        refs = set([(e['station_ref'], e.get('provider_ref', provider_ref)) for e in entries_set])
        for (ref, provider_ref) in refs:
            try:
                pk = station_finder.get_station_id(ref_provider=ref, provider_ref=provider_ref)
            except ValueError:
                LOG.warning('Station with ref_provider `%s` for provider `%s` not found in the database. All data for this station will be ignored.', ref, provider_ref)
            else:
                refs_to_ids[(ref, provider_ref)] = pk

        for entry in entries_set:
            ref_provider = entry.pop('station_ref')
            try:
                provider_ref = entry.pop('provider_ref')
            except KeyError:
                pass
            if (ref_provider, provider_ref) in refs_to_ids:
                entry['station_id'] = refs_to_ids[(ref_provider, provider_ref)]
                new_entries_set.append(entry)

        entries_set = new_entries_set

    return entries_set


def merge(entries_set):

    """
    Merge the entries set (being a list of dictionaries) so that all data with the same
    (station_id, time) pair are now one entry.
    """

    LOG.info("Merging...")
    station_time_keys = list(set([(e['station_id'], e['time']) for e in entries_set]))

    helper_dict = OrderedDict([(k, {}) for k in sorted(station_time_keys)])
    for entry in entries_set:
        helper_dict[(entry['station_id'], entry['time'])].update(entry)
    return helper_dict.values()


def remove_empty_entries(data):

    """
    From a list of data entries, remove those where all data values are null
    (i.e. 'time' and 'station_id' are the only keys with not-null value)
    """

    LOG.info('Removing entries with no observational data...')
    out_data = []
    for d in data:
        values = [v for k, v in d.items() if k not in ['time', 'station_id']]
        if any([v is not None for v in values]):
            out_data.append(d)
    LOG.info('%d entries removed, %d left', len(data) - len(out_data), len(out_data))
    return out_data


def main(argv_params=None):
    args = parse_args(argv_params)
    config = load_config(args.config)
    configure_logging(args.log_config)
    conn = WHConnection(config['db_url'])
    station_id_finder = StationFinder(conn)

    oi_parser = args.parser()

    if args.collate:
        data_for_merge = []

    for obs_file in args.files:
        LOG.info('Parsing file %s', obs_file)
        try:
            oi_parser.parse_file_name(os.path.abspath(obs_file))
        except ValueError as exc:
            LOG.warning('Improper file name %s. Omitting the file', os.path.abspath(obs_file))
            LOG.error(exc)
            continue

        with codecs.open(obs_file, encoding=args.encoding) as content:
            data = oi_parser.parse_sequence(content, args.ignore_broken_lines)
        meta = oi_parser.get_metadata()
        data_with_station_id = add_station_id(data, meta, station_id_finder)

        # verify if all of the observational values fall inside their range
        # check_data_sanity(data_with_station_id, fail_outside_range=not args.sanity_null_replace)
        # remove entries with no observational data
        data_with_station_id = remove_empty_entries(data_with_station_id)

        if args.collate:
            data_for_merge.extend(data_with_station_id)
        else:
            conn.chunk_insert_manage_duplicates(data_with_station_id, conn.get_table(args.table), chunk_size=100)

    if args.collate:
        merged_data = merge(data_for_merge)
        conn.chunk_insert_manage_duplicates(merged_data, conn.get_table(args.table), chunk_size=10000)


if __name__ == '__main__':
    main()
