from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from nose.tools import assert_equal, assert_raises, with_setup, assert_list_equal

from sqlalchemy import Table, Column, Integer, String, text
from util.db_connection import RowDuplicateError, update_missing_keys
from util.tests import make_WHConnection
from util.utilities import whLogger

LOG = whLogger(__name__)


def setup_table():
    """ Creates a fake_provider table to test with. """
    db_conn = make_WHConnection()
    Table('fake_provider', db_conn.metadata,
          Column('id', Integer, primary_key=True),
          Column('ref', String, unique=True),
          Column('name', String)
    )
    with db_conn.engine.begin() as conn:
        db_conn.metadata.create_all(db_conn.engine)


def teardown_table():
    """ Drops the fake_provider table created in setup() """
    db_conn = make_WHConnection()
    with db_conn.engine.begin() as conn:
        conn.execute('DROP TABLE fake_provider')


@with_setup(setup_table, teardown_table)
def test_context_manager_commit():
    db_conn = make_WHConnection()
    table = db_conn.get_table('fake_provider')

    with db_conn.trans() as wht:
        rows_from_before = len(wht.get_data(table.select()))
        wht.insert_single_entry({'ref': 'tr', 'name': 'Tru'}, table)
    with db_conn.trans() as wht:
        rows_after_commit = len(wht.get_data(table.select()))
    assert_equal(rows_from_before + 1, rows_after_commit)


@with_setup(setup_table, teardown_table)
def test_context_manager_rollback():
    db_conn = make_WHConnection()
    table = db_conn.get_table('fake_provider')
    try:
        with db_conn.trans() as wht:
            rows_from_before = len(wht.get_data(table.select()))
            wht.insert_single_entry({'ref': 'fk', 'name': 'Fake'}, table)
            raise ValueError()
    except ValueError:
        with db_conn.trans() as wht:
            rows_after_rollback = len(wht.get_data(table.select()))
            assert_equal(rows_from_before, rows_after_rollback)


@with_setup(setup_table, teardown_table)
def test_cm_insert_single_entry():
    db_conn = make_WHConnection()
    table = db_conn.get_table('fake_provider')
    entry = {'ref': 'test_cm', 'name': 'Test CM'}
    with db_conn.trans() as wht:
        pk = wht.insert_single_entry(entry, table)
    with db_conn.trans() as wht:
        rows = wht.get_data(text('SELECT * FROM fake_provider WHERE id = :pk'), pk=pk)
        assert_equal(1, len(rows))
        assert_equal(entry['ref'], rows[0]['ref'])
        assert_equal(entry['name'], rows[0]['name'])
    try:
        with db_conn.trans() as wht:
            wht.insert_single_entry(entry, table)
            assert False
    except RowDuplicateError:
        assert True


#@with_setup(setup_table, teardown_table)
def mk_test_entries(n=1000, ref_prefix='x', name_prefix='XYZ'):
    """ Creates test entries for fake_provider table """
    test_entries = []
    for x in range(n):
        test_entries.append({'ref': '%s%d' % (ref_prefix, x), 'name': '%s_%d' % (name_prefix, x)})
    return test_entries


@with_setup(setup_table, teardown_table)
def test_cm_bulk_insert():
    db_conn = make_WHConnection()
    table = db_conn.get_table('fake_provider')
    test_entries = mk_test_entries(1000)

    with db_conn.trans() as trans:
        trans.bulk_insert(test_entries, table)
    with db_conn.trans() as trans:
        count = trans.get_data('SELECT count(*) FROM fake_provider')[0][0]
        assert_equal(len(test_entries), count)
    with assert_raises(RowDuplicateError):
        with db_conn.trans() as trans:
            trans.bulk_insert(test_entries, table)
    with db_conn.trans() as trans:
        count = trans.get_data('SELECT count(*) FROM fake_provider')[0][0]
        assert_equal(len(test_entries), count)


@with_setup(setup_table, teardown_table)
def test_dbc_insert():
    test_entries = mk_test_entries()
    new_test_entries = mk_test_entries(10, 'a', 'ABC')
    new_test_entries.extend(test_entries[:15])
    db_conn = make_WHConnection()
    table = db_conn.get_table('fake_provider')

    db_conn.insert_data_cm(test_entries, table, bulk=True, auto_separate_insert=False)  #this should pass
    with db_conn.trans() as wht:
        count = wht.get_data('SELECT count(*) FROM fake_provider')[0][0]
        assert_equal(len(test_entries), count)

    # Try bulk insert on data partially in db (should fail)
    with assert_raises(RowDuplicateError):
        db_conn.insert_data_cm(new_test_entries, table, bulk=True, auto_separate_insert=False)
    with db_conn.trans() as wht:
        count = wht.get_data('SELECT count(*) FROM fake_provider')[0][0]
        assert_equal(len(test_entries), count)

    # Try row-by-row insert on data partially in db (should insert 10 of 25)
    db_conn.insert_data_cm(new_test_entries, table, bulk=False)
    with db_conn.trans() as wht:
        count = wht.get_data('SELECT count(*) FROM fake_provider')[0][0]
        assert_equal(len(test_entries) + 10, count)

    # Try bulk insert on data partially in DB, and then row-by-row insert on fail.
    new_test_entries.extend(mk_test_entries(5, 'd', 'DEF'))
    db_conn.insert_data_cm(new_test_entries, table, bulk=True, auto_separate_insert=True)
    with db_conn.trans() as wht:
        count = wht.get_data('SELECT count(*) FROM fake_provider')[0][0]
        assert_equal(len(test_entries) + 10 + 5, count)


@with_setup(setup_table, teardown_table)
def test_insert_duplicate_manage():
    db_conn = make_WHConnection()
    table = db_conn.get_table('fake_provider')
    entries_1 = mk_test_entries(10, 'a', 'ABC')
    entries_2 = mk_test_entries(5, 'a', 'ABC')
    entries_3 = mk_test_entries(10, 'b', 'BCD')
    entries = entries_1 + entries_2 + entries_3
    db_conn.chunk_insert_manage_duplicates(entries, table, chunk_size=10)
    with db_conn.trans() as wht:
        data = wht.get_data('select ref, name from fake_provider')
        assert_list_equal(data, [(e['ref'], e['name']) for e in entries_1 + entries_3])

def test_update_missing_keys():
    data = [
        {'time': '100', 'station_id': 1, 'temp': 45, 'wind_dir': 200},
        {'time': '200', 'station_id': 1, 'temp': 44, 'x': 'y'},
        {'time': '300', 'station_id': 3, 'temp': 38, 'wind_dir': 300, 'wind_speed': 7}
    ]
    expected = [
        {'time': '100', 'station_id': 1, 'temp': 45, 'wind_dir': 200, 'wind_speed': None, 'x': None},
        {'time': '200', 'station_id': 1, 'temp': 44, 'wind_dir': None, 'wind_speed': None, 'x': 'y'},
        {'time': '300', 'station_id': 3, 'temp': 38, 'wind_dir': 300, 'wind_speed': 7, 'x': None}
    ]
    assert_list_equal(expected, update_missing_keys(data))