"""

This script gets everything from `station` table and dumps it to a yaml file,
saved by default in the same folder with analogous name.

"""

import argparse
import os
import yaml
from sqlalchemy.sql import select
from util.db_connection import WHConnection
from util.utilities import load_config, configure_logging, whLogger


LOG = whLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='Config file for program with db_conn specified. Required.')
    parser.add_argument('--log-config', default=os.path.join(os.path.dirname(__file__), 'logging.yml'),
                        help='Config file for logging. Defaults to logging.yml in code folder.')
    parser.add_argument('--table', default='station', help='Station table, if different than `station`')

    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    configure_logging(args.log_config)
    db_conn = WHConnection(config['db_url'])

    t_station = db_conn.get_table(args.table)

    LOG.info('Getting all available data from `%s` table.', args.table)

    with db_conn.trans() as wht:
        data = wht.get_data(select([t_station]))

    data = [dict(d) for d in data]

    image_file = config.get('station_table_image', os.path.join(os.path.dirname(__file__), 'station_table_image.yml'))

    LOG.info('Saving `%s` table image to %s.', args.table, image_file)

    with open(image_file, 'w') as output:
        output.write(yaml.safe_dump(data, allow_unicode=True, width=1000))


if __name__ == '__main__':
    main()