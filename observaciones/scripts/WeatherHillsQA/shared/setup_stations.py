from __future__ import absolute_import, division, print_function, unicode_literals

import os
import argparse
import codecs
import yaml
import yaml.scanner
from util.db_connection import WHConnection, RowDuplicateError
from util.utilities import configure_logging, load_config, whLogger

LOG = whLogger(__name__)


def insert_provider_and_stations(db_conn, provider, stations):

    """
    Using db_conn, try to insert provider (given as dictionary) or fetch it from DB if already inserted,
    then insert stations so that it is ensured that new stations will be inserted and existing won't be reinserted.
    """

    try:
        with db_conn.trans() as trans:
            provider_id = trans.insert_single_entry(provider, db_conn.get_table('provider'))
            LOG.info('Inserted provider %s with ref %s', provider['name'], provider['ref'])
    except RowDuplicateError:
        with db_conn.trans() as trans:
            provider_id = trans.get_data('select id from provider where ref = :ref', ref=provider['ref'])[0][0]
            LOG.info('Fetched provider %s with ref %s already existing in DB', provider['name'], provider['ref'])

    for station in stations:
        station['provider_id'] = provider_id
    LOG.info('Found data for %d stations.', len(stations))

    db_conn.insert_data_cm(stations, db_conn.get_table('station'), auto_separate_insert=True)


def read_provider_and_stations(filename):

    """ Read provider and stations given in predefined yaml format. """

    LOG.info("Reading provider and stations from file %s" % filename)
    try:
        with codecs.open(filename, encoding='utf-8') as yml_file:
            data = yaml.safe_load(yml_file)
        return data['provider'], data['stations']
    except (IOError, KeyError, ValueError, yaml.scanner.ScannerError) as exc:
        LOG.error('Problem with reading from file. Does the file exist? Is it in the correct format?')
        LOG.exception(exc)
        raise


def dump_provider_and_stations(provider, stations, filename):

    """Dump provider and stations to a format readable by read_provider_and_stations"""

    entry = {'stations': stations, 'provider': provider}
    LOG.info('Dumping stations (%d) and provider to yaml file `%s`', len(stations), filename)
    with open(filename, 'w') as output:
        output.write(yaml.safe_dump(entry, allow_unicode=True, width=1000))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='Config file for program. Required')
    parser.add_argument('--log-config', default=os.path.join(os.path.dirname(__file__), 'logging.yml'),
                        help='Config file for logging. Defaults to logging.yml in code folder.')
    parser.add_argument('source_file', help='Yaml file with stations and provider')
    return parser.parse_args()


def main():
    args = parse_args()
    configure_logging(args.log_config)
    config = load_config(args.config)

    provider, stations = read_provider_and_stations(args.source_file)
    LOG.info('Loaded %d stations for provider %s', len(stations), provider['name'])

    db_conn = WHConnection(config['db_url'])
    insert_provider_and_stations(db_conn, provider, stations)


if __name__ == "__main__":
    main()