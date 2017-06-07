# encoding: utf-8

"""

Import observations data for Veðurstofa Íslands from stafli.

"""

from __future__ import absolute_import, division, print_function, unicode_literals
import os
import argparse
from sqlalchemy.sql import select, column, literal_column
from util.db_connection import WHConnection
from util.utilities import configure_logging, load_config, whLogger
from util.data_sanity import check_data_sanity
from util.calculator import parse_iso_date

LOG = whLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='Config file for program. Required')
    parser.add_argument('--log-config', default=os.path.join(os.path.dirname(__file__), 'logging.yml'),
                        help='Config file for logging. Defaults to logging.yml in code folder.')
    parser.add_argument('--start-date', type=parse_iso_date, help='Date to start copying observations from')
    return parser.parse_args()


def get_vi_stations(dest_conn):

    """ Get (ref_provider, id) pairs of Vedurstofan stations as present in station table """

    with dest_conn.trans() as wht:
        all_vi_stations = wht.get_data("select ref_provider, id, manual from station where ref like 'vi.is.%%'")
    return all_vi_stations


def build_import_query(db_conn, table_name, station, start_date):

    """
    Build SQLAlchemy query to obtain data from source table, with labels referring to
    our destination observation table
    """

    t = db_conn.get_table(table_name)
    columns = [
        t.c.timi.label('time'),
        t.c.f.label('wind_speed'),
        t.c.fg.label('wind_gust'),
        t.c.d.label('wind_dir'),
        t.c.t.label('temp'),
        t.c.p.label('pressure'),
        t.c.rh.label('rel_hum'),
        literal_column(str(station['id'])).label('station_id')
    ]
    q = select(columns).where(t.c.stod == station['ref_provider'])
    if start_date:
        q = q.where(t.c.timi >= start_date)
    return q


def get_external_observations(source_conn, station, start_date):

    """ Get observations from one of two tables on `forecasts` database, for a concrete station """

    table = 'ath' if station['manual'] else 'sj_klst'
    with source_conn.trans() as wht:
        result = wht.get_data(build_import_query(source_conn, table, station, start_date))

    LOG.info('Received %d rows from table %s', len(result), table)
    return [dict(row) for row in result]


def main():
    args = parse_args()
    config = load_config(args.config)
    configure_logging(args.log_config)
    source_conn = WHConnection(config['db_url_source'])
    dest_conn = WHConnection(config['db_url_dest'])

    all_vi_stations = get_vi_stations(dest_conn)

    if args.start_date:
        LOG.info('Ignoring data older than %s', args.start_date)
    for i, station in enumerate(all_vi_stations):
        LOG.info('Processing station with ref_provider `%s` (%d/%d)', station['ref_provider'], (i + 1), len(all_vi_stations))

        result = get_external_observations(source_conn, station, args.start_date)

        # verify the odd observations (presumably indicating nodata) existing in source data, replacing them with None
        check_data_sanity(result, fail_outside_range=False, log_warning=False)

        dest_conn.chunk_insert_manage_duplicates(result, dest_conn.get_table('observation'), 10000)


if __name__ == '__main__':
    main()
