# encoding: utf-8

"""

Classes for managing communication with the database.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import re
from sqlalchemy import Table, MetaData, create_engine, text
from sqlalchemy.sql import insert, select, label
from sqlalchemy.exc import IntegrityError, OperationalError, ArgumentError, NoSuchTableError, ProgrammingError
from util.utilities import whLogger

LOG = whLogger(__name__)


class RowDuplicateError(IntegrityError):
    def __init__(self, e):
        super(RowDuplicateError, self).__init__(e.statement, e.params, e.orig, e.connection_invalidated)

    def __str__(self):
        string = super(RowDuplicateError, self).__str__()
        return string[:1000] + (' (...)' if len(string) > 1000 else '')

    def __repr__(self):
        return super(RowDuplicateError, self).__repr__()


class WHTransaction(object):

    """
    This class encapsulates a single transaction on a connection to the WeatherHills database.
    It is usually created as a context manager with a WeatherDBConn object as:

    db_conn = WeatherDBConn()
    with db_conn as wht:
        wht.do_work()

    This will take care of committing transactions if all went well or rolling them back if
    an exception was raised.
    """

    def __init__(self, conn, trans):
        super(WHTransaction, self).__init__()

        self.conn = conn
        """ :type: Connection """

        self.trans = trans
        """ :type: Transaction """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            LOG.warn('Rolling back transaction on exception %s', exc_val)
            LOG.exception(exc_tb)
            self.trans.rollback()
        else:
            LOG.debug('Committing transaction')
            self.trans.commit()
        self.conn.close()

    def execute(self, query, *args, **kwargs):

        """
        Wraps conn.execute so that it doesn't need to be called from outside.
        Mainly to control kwargs passing (put text() around the query string if necessary)
        """

        if type(query) in (unicode, str) and kwargs:
            query = text(query)
        try:
            result = self.conn.execute(query, *args, **kwargs)
        except ProgrammingError as exc:
            LOG.error('Problem with query. %s', exc.message)
            raise
        return result

    def get_data(self, query, *args, **kwargs):

        """
        Execute given query (sqlalchemy-like or sql string) in a single transaction.

        :return: A list of row-proxies. Empty result is passed silently to be handled outside this function.
        """

        return self.execute(query, *args, **kwargs).fetchall()

    def insert_single_entry(self, datum, table):
        try:
            result = self.conn.execute(insert(table, datum))
            if result.inserted_primary_key:
                return result.inserted_primary_key[0]
            else:
                return None
        except IntegrityError as exc:
            if 'duplicate key value' in exc.message:
                raise RowDuplicateError(exc)
            else:
                raise

    def bulk_insert(self, data, table):
        chunk_size = 10000
        data_chunks = [data[x:x+chunk_size] for x in range(0, len(data), chunk_size)]

        try:
            inserted_entries = 0
            for chunk in data_chunks:
                self.conn.execute(insert(table, chunk))
                inserted_entries += len(chunk)
                LOG.debug('Inserted %d of %d entries', inserted_entries, len(data))
        except IntegrityError as exc:
            if 'duplicate key value' in exc.message:
                LOG.error('Duplicate found, data not inserted.')
                raise RowDuplicateError(exc)
            else:
                LOG.error('Integrity error in DB %s', exc)
                raise


def update_missing_keys(list_of_dicts):

    """
    Make each dict in list of dicts contain the same set of keys.
    If there was no value for that key, it is added and its value set to None.
    This is required as SQLAlchemy tends to weirdly replace such
    missing keys with values from unknown sources.
    """

    LOG.info('Making sure all (%d) entries have the same keys set...', len(list_of_dicts))
    all_keys = set().union(*[d.keys() for d in list_of_dicts])
    for d in list_of_dicts:
        keys_to_fill = all_keys - set(d.keys())
        for key in keys_to_fill:
            d[key] = None
    return list_of_dicts


class WHConnection(object):

    """
    Class for managing a connection with database. ...
    """

    def __init__(self, url):
        """

        :param url: DB url in a form postgresql://usr:pass@host/database
        :raise:
        """
        try:
            self.engine = create_engine(url)

            # This dummy thing is to check if engine was correctly connected to the db. Figure out how to do it nicely...
            with self.engine.begin() as conn:
                conn.execute('select 1')

        except (OperationalError, ArgumentError) as exc:
            LOG.error('Database failed to load, %s', repr(exc).strip())
            raise ValueError('Database failed to load.', exc.message.strip())
        self.metadata = MetaData()
        self.active_tables = {}

    def trans(self):

        """ This object is a factory for WHTransaction context managers. """

        conn = self.engine.connect()
        trans = conn.begin()
        return WHTransaction(conn, trans)

    def get_table(self, table_name):

        """Return a sqlalchemy reference to a table in DB. If the table wasn't referenced before, it is loaded to memory

        :param table_name: name of the table in the DB
        :return: table
        :raise: sqlalchemy.exc.NoSuchTableError

        """

        if not table_name in self.active_tables:
            try:
                self.active_tables[table_name] = Table(table_name, self.metadata, autoload=True, autoload_with=self.engine)
            except NoSuchTableError as e:
                LOG.error('Table %s does not exist, error: %s', table_name, repr(e).strip())
                raise

        return self.active_tables[table_name]

    def chunk_insert_manage_duplicates(self, data, table, chunk_size=500):

        """
        Insert data in small chunks. If a particular chunk insert fails due to a
        RowDuplicateError, insert its content row-by-row.
        """

        data = update_missing_keys(data)
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        inserted = 0
        duplicates = 0
        LOG.info('Inserting %d entries in %d chunk(s) of maximal size %d', len(data), len(chunks), chunk_size)
        for (i, chunk) in enumerate(chunks):
            try:
                with self.trans() as wht:
                    wht.bulk_insert(chunk, table)
                    inserted += len(chunk)
                    LOG.debug('(%d/%d) Successfully inserted %d items ', (i + 1), len(chunks), len(chunk))
            except RowDuplicateError as e:
                inserted_here = 0
                duplicates_here = 0
                for entry in chunk:
                    try:
                        with self.trans() as wht:
                            wht.insert_single_entry(entry, table)
                            inserted_here += 1
                    except RowDuplicateError:
                        duplicates_here += 1
                    except BaseException as exc:
                        LOG.error('Error in DB insert %s', exc)
                        raise
                inserted += inserted_here
                duplicates += duplicates_here
                LOG.debug('(%d/%d) Row-by-row insert: %d inserted, %d duplicates', (i + 1), len(chunks), inserted_here, duplicates_here)
        LOG.info('Total %d entries inserted, %d duplicates' % (inserted, duplicates))

    def insert_data_cm(self, data, table, bulk=True, auto_separate_insert=False):

        """
        Insert given data to given table.

        :param data: a list of entries, each entry is a dictionary with keys reflecting table columns
        :param table: target table
        :param bulk: should data be inserted all at once or each entry separate
        :param auto_separate_insert: if bulk insert resulted in a transaction rolled back because of duplicate found,
        having this set makes row-by-row insert tried automatically
        """

        data = update_missing_keys(data)
        try_non_bulk = True
        LOG.info('Inserting %d values to DB...' % len(data))
        if bulk:
            try:
                with self.trans() as wht:
                    wht.bulk_insert(data, table)
                try_non_bulk = False
            except RowDuplicateError:
                if not auto_separate_insert:
                    raise
                LOG.info('Trying to insert row by row...')

        if try_non_bulk:
            inserted = 0
            duplicates = 0
            for entry in data:
                try:
                    with self.trans() as wht:
                        wht.insert_single_entry(entry, table)
                        inserted += 1
                except RowDuplicateError:
                    duplicates += 1
                except BaseException as exc:
                    LOG.error('Error in DB insert', exc)
                    raise

            LOG.info('%d entries inserted, %d duplicates' % (inserted, duplicates))


class StationFinder(object):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def get_station_id(self, ref=None, ref_provider=None, provider_ref=None):

        """
        Return database station ID for reference in data table queries (e.g. observation table...)

        Either ref (a DB reference given by us) or ref_provider (how the provider marks that station) should be present.
        Provider_ref can be useful if ref_provider used, which can be non-unique between providers.
        """

        if not ref and not ref_provider:
            raise ValueError('No reference given')

        stations = self.db_conn.get_table('station')
        query = select([stations.c.id])
        if ref:
            query = query.where(stations.c.ref == ref)
        if ref_provider:
            query = query.where(stations.c.ref_provider == ref_provider)
        if provider_ref:
            providers = self.db_conn.get_table('provider')
            query = query.where(stations.c.provider_id==providers.c.id).where(providers.c.ref == provider_ref)
        with self.db_conn.trans() as trans:
            result = trans.get_data(query)
        if len(result) > 1:
            log_msg = 'Ambiguous result for ref={0}, ref_provider={1}, provider_ref={2}'.format(ref, ref_provider, provider_ref)
            LOG.error(log_msg)
            error_msg = 'Multiple results given. The given reference was true for more than one station. '
            error_msg += 'Try to include a provider reference.' if not provider_ref else ''
            raise ValueError(error_msg)

        if len(result) == 0:
            log_msg = 'No result for ref={0}, ref_provider={1}, provider_ref={2}'.format(ref, ref_provider, provider_ref)
            LOG.error(log_msg)
            error_msg = 'No result for the given identifiers. '
            if ref and ref_provider:
                error_msg += 'Try to use only either ref or ref_provider.'
            raise ValueError(error_msg)

        return result[0][0]

    def find_ids(self, regexp, param, provider_ref=None):

        """
        Find station IDs based on a regular expression, which can be checked against either 'ref' or 'ref_provider'

        :param regexp: Regular expression to filter stations.
        :param param: Should be either 'ref' or 'ref_provider'.
        :param provider_ref: Optional reference of the provider.
        :return: A list of found station ids.
        """

        if param not in ['ref', 'ref_provider']:
            raise ValueError("Param should equal either 'ref' or 'ref_provider'")

        found_ids = []
        station = self.db_conn.get_table('station')
        provider = self.db_conn.get_table('provider')
        query = select([station.c.id,
                        station.c.ref,
                        station.c.ref_provider,
                        label('provider_ref', provider.c.ref)],
                station.c.provider_id==provider.c.id)
        with self.db_conn.trans() as trans:
            values = trans.get_data(query)

        for item in values:
            if provider_ref and provider_ref != item['provider_ref']:
                continue
            if re.match(regexp, item[param]):
                found_ids.append(item['id'])
        return found_ids

    def get_ref(self, pk):
        station = self.db_conn.get_table('station')
        query = select([station.c.ref]).where(station.c.id==pk)
        with self.db_conn.trans() as trans:
            ref = trans.get_data(query)
        try:
            return ref[0][0]
        except IndexError:
            return None

    def all_stations(self, provider_ref=None, columns=('ref', 'id')):
        station = self.db_conn.get_table('station')
        provider = self.db_conn.get_table('provider')
        try:
            cols = [getattr(station.c, col) for col in columns]
        except AttributeError:
            cols = [getattr(station.c, col) for col in ('ref', 'id')]
        query = select(cols, station.c.provider_id == provider.c.id)
        if provider_ref:
            query = query.where(provider.c.ref == provider_ref)
        with self.db_conn.trans() as trans:
            values = trans.get_data(query)
        return list(values)