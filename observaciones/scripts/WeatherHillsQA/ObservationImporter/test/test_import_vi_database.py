from datetime import datetime
from mock import MagicMock
from sqlalchemy import Table, Column, Integer, String
from util.db_connection import WHConnection
from import_vi_database import get_external_observations, build_import_query
import import_vi_database

from unittest import TestCase


def build_vi_alike_table(db_conn, table_name):
    return Table(table_name, db_conn.metadata,
        Column('timi', String),
        Column('f', Integer),
        Column('fg', Integer),
        Column('d', Integer),
        Column('t', Integer),
        Column('p', Integer),
        Column('rh', Integer),
        Column('stod', Integer),
    )


class TestVIImport(TestCase):
    def setUp(self):
        self.db_conn = WHConnection('sqlite://')
        self.fake_ath_ath = build_vi_alike_table(self.db_conn, 'fake_ath_ath')
        self.fake_ath_sj_klst = build_vi_alike_table(self.db_conn, 'fake_ath_sj_klst')

        with self.db_conn.engine.begin():
            self.db_conn.metadata.create_all(self.db_conn.engine)

        self.for_ath_ath = [
            {'timi': str(datetime.now()), 'f': 10, 'fg': 11, 'd': 100, 't': 5, 'p': 999, 'rh': 77, 'stod': 5},
            {'timi': str(datetime.now()), 'f': 12, 'fg': 13, 'd': 101, 't': 7, 'p': 1000, 'rh': 78, 'stod': 6},
            {'timi': str(datetime.now()), 'f': 14, 'fg': 15, 'd': None, 't': None, 'p': None, 'rh': None, 'stod': 7},
        ]
        self.for_ath_sj_klst = [
            {'timi': str(datetime.now()), 'f': 20, 'fg': 21, 'd': 200, 't': 25, 'p': 1009, 'rh': 87, 'stod': 107},
            {'timi': str(datetime.now()), 'f': 22, 'fg': 23, 'd': 201, 't': 27, 'p': 1010, 'rh': 88, 'stod': 108},
            {'timi': str(datetime.now()), 'f': 24, 'fg': 25, 'd': None, 't': None, 'p': None, 'rh': None, 'stod': 109},
        ]
        with self.db_conn.trans() as trans:
            trans.bulk_insert(self.for_ath_ath, self.fake_ath_ath)
            trans.bulk_insert(self.for_ath_sj_klst, self.fake_ath_sj_klst)

    def tearDown(self):
        with self.db_conn.engine.begin() as conn:
            conn.execute('DROP TABLE fake_ath_ath')
            conn.execute('DROP TABLE fake_ath_sj_klst')

    def test_get_external_observations(self):
        import_vi_database.build_import_query = MagicMock()
        import_vi_database.build_import_query.return_value = 'select * from fake_ath_ath limit 0'
        station = {'id': 999, 'ref': '999', 'manual': True}
        get_external_observations(self.db_conn, station, None)
        import_vi_database.build_import_query.assert_called_with(self.db_conn, 'ath', station, None)
        station = {'id': 999, 'ref': '999', 'manual': False}
        get_external_observations(self.db_conn, station, None)
        import_vi_database.build_import_query.assert_called_with(self.db_conn, 'sj_klst', station, None)

    def test_build_query(self):
        written_query = 'select timi as time, f as wind_speed, fg as wind_gust, d as wind_dir, ' \
                        't as temp, p as pressure, rh as rel_hum, 111 as station_id from fake_ath_sj_klst where stod=7'

        built_query = build_import_query(self.db_conn, 'fake_ath_sj_klst', {'id': 111, 'ref_provider': 7}, None)
        with self.db_conn.trans() as wht:
            expected = wht.get_data(written_query)
            actual = wht.get_data(built_query)

        self.assertListEqual(expected, actual)

    def test_query_start_date(self):
        other_data = [
            {'timi': str(datetime.now()), 'f': 20, 'fg': 21, 'd': 200, 't': 25, 'p': 1009, 'rh': 87, 'stod': 111},
            {'timi': str(datetime.now()), 'f': 22, 'fg': 23, 'd': 201, 't': 27, 'p': 1010, 'rh': 88, 'stod': 111},
            {'timi': str(datetime.now()), 'f': 24, 'fg': 25, 'd': None, 't': None, 'p': None, 'rh': None, 'stod': 111},
        ]
        with self.db_conn.trans() as trans:
            trans.bulk_insert(other_data, self.fake_ath_sj_klst)
        query = build_import_query(self.db_conn, 'fake_ath_sj_klst', {'id': 111, 'ref_provider': 111}, other_data[1]['timi'])
        with self.db_conn.trans() as wht:
            actual = [dict(r) for r in wht.get_data(query)]
        expected = [
            {'time': other_data[1]['timi'], 'wind_speed': 22, 'wind_gust': 23, 'wind_dir': 201, 'temp': 27, 'pressure': 1010, 'rel_hum': 88, 'station_id': 111},
            {'time': other_data[2]['timi'], 'wind_speed': 24, 'wind_gust': 25, 'wind_dir': None, 'temp': None, 'pressure': None, 'rel_hum': None, 'station_id': 111}
        ]
        self.assertListEqual(expected, actual)
