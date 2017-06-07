from __future__ import absolute_import, division, print_function, unicode_literals
from nose.tools import assert_set_equal

from util.tests import test_config
from util.db_tables import *


def test_create_tables():
    seen_tables = []
    engine = create_engine(test_config['db_url'])
    metadata = create_tables(engine)
    try:
        with engine.begin() as conn:
            for table in metadata.tables.values():
                seen_tables.append(table.name)
                conn.execute(table.select())

        assert_set_equal(set(seen_tables), {'observation', 'station', 'provider', 'grid_forecast_data',
                                            'grid_point', 'grid', 'grid_forecast', 'schedule',
                                            'point_forecast_data', 'wind_power', 'observation_quality', 'point_forecast'})
    finally:
        with engine.begin() as conn:
            metadata.drop_all(conn)
