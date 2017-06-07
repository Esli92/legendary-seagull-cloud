# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals
from unittest import TestCase

import sqlalchemy

from util.db_connection import *
from util.db_tables import create_tables
from util.tests import make_WHConnection


class TestStationFinder(TestCase):
    def setUp(self):
        #create tables if missing
        self.db_conn = make_WHConnection()
        create_tables(self.db_conn.engine)

        #create a fake provider
        self.provider_ids_to_drop = []
        example_provider = {'ref': 'zyx.pl', 'name': 'Mr. Zyx'}
        provider_table = self.db_conn.get_table('provider')
        try:
            with self.db_conn.trans() as trans:
                p_pk = trans.insert_single_entry(example_provider, provider_table)
                self.provider_ids_to_drop.append(p_pk)
        except RowDuplicateError:  # then we wouldn't drop that one
            with self.db_conn.trans() as trans:
                p_pk = trans.get_data('select id from provider where ref = :ref', ref=example_provider['ref'])[0][0]
        #create a set of fake stations
        self.station_ids_to_drop = []
        station_table = self.db_conn.get_table('station')
        for i in range(1, 51):
            entry = {'ref': 'zyx.pl.%d' % i,
                     'name': 'Zyx %d station',
                     'lon': 0.1 * i,
                     'lat': 50 + i,
                     'provider_id': p_pk,
                     'ref_provider': '%d_ZYX' % i}
            try:
                with self.db_conn.trans() as trans:
                    s_pk = trans.insert_single_entry(entry, station_table)
                    self.station_ids_to_drop.append(s_pk)
            except RowDuplicateError:
                pass

        self.finder = StationFinder(self.db_conn)

    def tearDown(self):
        with self.db_conn.trans() as trans:
            for x in self.station_ids_to_drop:
                try:
                    trans.execute('delete from station where id = :id', id=x)
                except BaseException as ex:
                    print (ex)
            for x in self.provider_ids_to_drop:
                trans.execute('delete from provider where id = :id', id=x)



    def test_find_ids_by_ref_and_ref_provider(self):
        for key in ['ref', 'ref_provider']:
            with self.db_conn.trans() as trans:
                rows = trans.get_data('select %s from station' % key) #TODO how to change it to arg or kwarg?

            patterns_to_try = set()
            for row in rows:
                pattern = re.search('^(.).*', row[key]).group(1)
                patterns_to_try.add(pattern)
            for pattern in patterns_to_try:
                query = "select id from station where %s like '%s%%'" % (key, pattern)
                with self.db_conn.trans() as trans:
                    rows = trans.get_data(sqlalchemy.text(query))
                if not rows[0]:
                    raise ValueError('Empty station list, test cannot run')
                expected = [row[0] for row in rows]
                result = self.finder.find_ids('%s.*' % pattern, key)
                self.assertEqual(sorted(expected), sorted(result))

    def test_wrong_key_attribute(self):
        self.assertRaises(ValueError, self.finder.find_ids, param='place', regexp='.*')

    def test_get_ref_existing(self):
        query = 'select id, ref from station'
        with self.db_conn.trans() as trans:
            results = trans.get_data(query)
        if not results[0]:
            raise ValueError('Empty station list, test not able to run')
        for result in results:
            actual = self.finder.get_ref(result['id'])
            self.assertEqual(result['ref'], actual)

    def test_get_ref_non_existing(self):
        actual = self.finder.get_ref(-1)
        self.assertEqual(None, actual)

    def test_get_station_id(self):
        sql = 'select s.ref, s.ref_provider, p.ref as provider_ref, s.id from station s join provider p on s.provider_id=p.id'
        with self.db_conn.trans() as trans:
            rows = trans.get_data(sql)

        for row in rows:
            expected = row['id']
            try:
                actual1 = self.finder.get_station_id(ref=row['ref'])
            except ValueError as exc:
                if 'Multiple results given' in exc.message:
                    actual1 = self.finder.get_station_id(ref=row['ref'], provider_ref=row['provider_ref'])
                else:
                    raise
            try:
                actual2 = self.finder.get_station_id(ref_provider=row['ref_provider'])
            except ValueError as exc:
                if 'Multiple results given' in exc.message:
                    actual1 = self.finder.get_station_id(ref=row['ref_provider'], provider_ref=row['provider_ref'])
                else:
                    raise
            self.assertEqual(expected, actual1)
            self.assertEqual(expected, actual2)

