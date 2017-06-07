# encoding: utf-8

"""

Integration test of parsers including inserting appropriate data into database
and comparing inserted data to expected values.

"""

from __future__ import absolute_import, division, print_function, unicode_literals
import os
import glob
from unittest import TestCase
from datetime import datetime
from util.db_tables import create_tables
from util.tests import make_WHConnection, project_path
from util.utilities import utc
import import_files


def setup_database_contents(db_conn, provider, stations):
    create_tables(db_conn.engine)
    inserted_stations = {}
    with db_conn.trans() as trans:
        ppk = trans.insert_single_entry(provider, db_conn.get_table('provider'))
        inserted_provider_id = ppk
        station_tab = db_conn.get_table('station')
        for station in stations:
            station.update({'provider_id': ppk})
            pk = trans.insert_single_entry(station, station_tab)
            inserted_stations.update({station['ref']: pk})
    return inserted_provider_id, inserted_stations


def teardown_database_contents(db_conn, inserted_provider_id, inserted_stations):
    with db_conn.trans() as trans:
        for x in inserted_stations.values():
            try:
                trans.execute('delete from observation where station_id = :id', id=x)
            except BaseException as ex:
                print (ex)

        for x in inserted_stations.values():
            try:
                trans.execute('delete from wind_power where station_id = :id', id=x)
            except BaseException as ex:
                print (ex)
        for x in inserted_stations.values():
            try:
                trans.execute('delete from station where id = :id', id=x)
            except BaseException as ex:
                print (ex)

        trans.execute('delete from provider where id = :id', id=inserted_provider_id)


class ImportLandsverkFOFilesTest(TestCase):
    def setUp(self):
        self.db_conn = make_WHConnection()
        provider = {'ref': 'lv.fo', 'name': 'Landsverk'}
        stations = [
            {'ref': 'lv.fo.100', 'ref_provider': 'F100', 'lon': 1, 'lat': 51, 'name': 'Fake 100'},
            {'ref': 'lv.fo.200', 'ref_provider': 'F200', 'lon': 2, 'lat': 52, 'name': 'Fake 200'},
            {'ref': 'lv.fo.300', 'ref_provider': 'F300', 'lon': 3, 'lat': 53, 'name': 'Fake 300'},
            {'ref': 'lv.fo.34', 'ref_provider': 'F34', 'lon': 34, 'lat': 34, 'name': 'Fake 34'}
        ]
        self.inserted_provider_id, self.inserted_stations = setup_database_contents(self.db_conn, provider, stations)

    def tearDown(self):
        teardown_database_contents(self.db_conn, self.inserted_provider_id, self.inserted_stations)

    def test_import_faroe_files(self):
        config_path = os.path.join(project_path, 'test_config.yml')
        test_dir = os.path.join(os.path.dirname(__file__), 'data/landsverk_fo')
        files = []
        for a in os.walk(test_dir):
            for i in [fn for fn in a[2] if fn.endswith('.phx')]:
                filename = os.path.join(a[0], i)
                files.append(filename)

        if not files:
            self.fail('No test files found in %s' % test_dir)

        files_vaisala = [f for f in files if 'F34' not in f.split(os.sep)[-2]]
        files_f34 = [f for f in files if 'F34' in f.split(os.sep)[-2]]

        options = ['--parser', 'LandsverkVaisalaObservationParser', '--config', config_path]
        options.extend(files_vaisala)
        import_files.main(options)

        options = ['--parser', 'LandsverkF34ObservationParser', '--config', config_path]
        options.extend(files_f34)
        import_files.main(options)

        def rang(x, y, step):
            return [r / 10000.0 for r in range(int(round(x * 10000)), int(round(y * 10000)), int(round(step * 10000)))]

        with self.db_conn.trans() as trans:
            exact_data = trans.get_data('select * from observation order by temp')
            self.assertEqual(80, len(exact_data))

            temperatures = [line['temp'] for line in exact_data]
            exp_temp = rang(1.01, 1.21, 0.01) + rang(2.01, 2.21, 0.01) + rang(3.01, 3.21, 0.01) + rang(5.01, 5.21, 0.01)
            self.assertListEqual(exp_temp, temperatures)

            exp_rel_hum = rang(10.01, 10.21, 0.01) + rang(20.01, 20.21, 0.01) + rang(30.01, 30.21, 0.01) + rang(50.01, 50.21, 0.01)
            self.assertListEqual(exp_rel_hum, [line['rel_hum'] for line in exact_data])

            exp_wind_spd = rang(1.001, 1.021, 0.001) + rang(2.001, 2.021, 0.001) + rang(3.001, 3.021, 0.001) + rang(5.001, 5.021, 0.001)
            self.assertListEqual(exp_wind_spd, [line['wind_speed'] for line in exact_data])

            exp_wind_dir = map(float, range(100, 120) + range(200, 220) + range(300, 320) + range(50, 70))
            self.assertListEqual(exp_wind_dir, [line['wind_dir'] for line in exact_data])

            exp_pres = map(float, range(1001, 1021) + range(901, 921) + range(801, 821) + range(1001, 1021))
            self.assertListEqual(exp_pres, [line['pressure'] for line in exact_data])

            exp_gust = rang(1.005, 1.105, 0.005) + rang(2.005, 2.105, 0.005) + rang(3.005, 3.105, 0.005) + rang(5.005, 5.105, 0.005)
            self.assertListEqual(exp_gust, [line['wind_gust'] for line in exact_data])

            temps_road = [line['temp_road'] for line in exact_data]
            true_temps_road = [(i, val) for (i, val) in zip(range(len(temps_road)), temps_road) if val is not None]
            self.assertEqual([(40, 8.88), (59, 4.0)], true_temps_road)

            exp_id = [self.inserted_stations['lv.fo.100']] * 40 + [self.inserted_stations['lv.fo.300']] * 20 + [self.inserted_stations['lv.fo.34']] * 20
            self.assertEqual(exp_id, [line['station_id'] for line in exact_data])


class ImportVegagerdinFilesTest(TestCase):
    def setUp(self):
        self.db_conn = make_WHConnection()
        provider = {'ref': 'vg.is', 'name': 'Vegagerdin'}
        stations = [
            {'ref': 'vg.is.72', 'ref_provider': '72', 'lon': 1, 'lat': 51, 'name': 'Akrafjall'},
            {'ref': 'vg.is.39', 'ref_provider': '39', 'lon': 2, 'lat': 52, 'name': 'Ennishals'},
            {'ref': 'vg.is.22', 'ref_provider': '22', 'lon': 3, 'lat': 53, 'name': 'Frodarheidi'},
        ]
        self.inserted_provider_id, self.inserted_stations = setup_database_contents(self.db_conn, provider, stations)

    def tearDown(self):
        teardown_database_contents(self.db_conn, self.inserted_provider_id, self.inserted_stations)

    def test_import_vegagerdin_files(self):
        config_path = os.path.join(project_path, 'test_config.yml')
        test_dir = os.path.join(os.path.dirname(__file__), 'data/vegagerdin')
        files = []
        for filename in glob.glob(os.path.join(test_dir, 'v_*')):
            files.append(filename)

        if not files:
            self.fail('No test files found in %s' % test_dir)

        options = ['--parser', 'VegagerdinObservationParser', '--config', config_path]
        options.extend(files)
        import_files.main(options)

        ts_0 = datetime(2013, 3, 1, tzinfo=utc)
        ts_1 = datetime(2013, 3, 1, 0, 10, tzinfo=utc)
        ts_2 = datetime(2013, 3, 1, 0, 20, tzinfo=utc)

        exp_station_id = [self.inserted_stations['vg.is.72']] + [self.inserted_stations['vg.is.39']] * 2 + [self.inserted_stations['vg.is.22']] * 2

        with self.db_conn.trans() as trans:
            exact_data = trans.get_data('select * from observation order by station_id, time')
            self.assertEqual(5, len(exact_data))
            self.assertListEqual([7.239, 3.229, 3.204, 4.951, 4.789], [line['temp'] for line in exact_data])
            self.assertListEqual([38.74, 182.7, 182.8, 143.2, 126.4], [line['wind_dir'] for line in exact_data])
            self.assertListEqual([2.675, 9.62, 9.39, 4.107, 3.525], [line['wind_speed'] for line in exact_data])
            self.assertListEqual([7.546, 11.76, 12.35, 10.98, 7.74], [line['wind_gust'] for line in exact_data])
            self.assertListEqual([5.526, -0.049, -0.053, 2.825, 2.897], [line['temp_road'] for line in exact_data])
            self.assertListEqual([92.6, 100.0, 100.0, 100.0, 100.0], [line['rel_hum'] for line in exact_data])
            self.assertListEqual([None, None, None, None, None], [line['pressure'] for line in exact_data])
            self.assertListEqual(exp_station_id, [line['station_id'] for line in exact_data])
            self.assertListEqual([ts_0, ts_1, ts_2, ts_1, ts_2], [line['time'] for line in exact_data])


class ImportVedurstofanCsvFilesTest(TestCase):
    def setUp(self):
        self.db_conn = make_WHConnection()
        provider = {'ref': 'vi.is', 'name': 'Vedurstofa Islands'}
        stations = [
            {'ref': 'vi.is.178', 'ref_provider': '178', 'lon': 1, 'lat': 1, 'name': 'VI IS 178'},
            {'ref': 'vi.is.252', 'ref_provider': '252', 'lon': 1, 'lat': 1, 'name': 'VI IS 252'},
            {'ref': 'vi.is.990', 'ref_provider': '990', 'lon': 1, 'lat': 1, 'name': 'VI IS 990'},
            {'ref': 'vi.is.6208', 'ref_provider': '6208', 'lon': 1, 'lat': 1, 'name': 'VI IS 6208'},
            {'ref': 'vi.is.7476', 'ref_provider': '7476', 'lon': 1, 'lat': 1, 'name': 'VI IS 7476'},
            {'ref': 'vi.is.2304', 'ref_provider': '2304', 'lon': 1, 'lat': 1, 'name': 'VI IS 2304'},
        ]

        self.inserted_provider_id, self.ins_stations = setup_database_contents(self.db_conn, provider, stations)

    def tearDown(self):
        teardown_database_contents(self.db_conn, self.inserted_provider_id, self.ins_stations)

    def test_import_vedurstofan_files(self):
        config_path = os.path.join(project_path, 'test_config.yml')
        test_dir = os.path.join(os.path.dirname(__file__), 'data/vedurstofan')
        files = []
        for filename in glob.glob(os.path.join(test_dir, '*.csv')):
            files.append(filename)

        if not files:
            self.fail('No test files found in %s' % test_dir)

        options = ['--parser', 'VedurstofanCsvObservationParser', '--config', config_path]
        options.extend(files)
        import_files.main(options)

        ts_0 = datetime(2010, 9, 3, tzinfo=utc)
        ts_1 = datetime(2010, 9, 4, tzinfo=utc)
        ts_2 = datetime(2010, 9, 5, tzinfo=utc)

        ts_3 = datetime(2010, 9, 3, 3, tzinfo=utc)
        ts_4 = datetime(2010, 9, 4, 3, tzinfo=utc)
        ts_5 = datetime(2010, 9, 5, 3, tzinfo=utc)

        exp_station_id = [self.ins_stations['vi.is.178']] * 3 + [self.ins_stations['vi.is.252']] * 3 + [self.ins_stations['vi.is.990']] * 3
        exp_station_id += [self.ins_stations['vi.is.6208']] * 6 + [self.ins_stations['vi.is.7476']] * 4 + [self.ins_stations['vi.is.2304']] * 6

        exp_temp = [13.5, 14, 13.4, 13.9, 11.2, 12.5, 12.2, 13.1, 13.3, 14.2, 14.2, 14.7, 14.7, 14, 14,  12.4, 12.4, 14, 14, 15.3, 15.3, 13.4, 13.4, 10.9, 10.9]
        exp_wind_dir = [110, 90, 110, 20, 230, 190, 110, 60, 90, 111, 111, 79, 79, 86, 86,  173, 173, 20, 20, None, None, 299, 299, 106, 106]
        exp_wind_speed = [5.4, 4.6, 9.3, 1.4, 7.7, 0.6, 21.8, 11.8, 9.3, 5, 5, 8.2, 8.2, 3.8, 3.8,  2.8, 2.8, 0.5, 0.5, None, None, 1.3, 1.3, 1.6, 1.6]
        exp_wind_gust = [14.8, None, None, 2.2, None, 5.8, 26.7, 19, 16.5, 9.6, None, 10.7, None, 5.4,  None, 5.4, None, 3.3, None, None, None, 1.8, None, 2.5, None]
        exp_pressure = [1010.3, 1010.6, 1011.1, 1011, 1014.6, 1012.3, 1008.8, None, 1007.9,  None, None, None, None, None, None, 1009, None, None, None, 1009.5, None, None, None, None, None]
        exp_rel_hum = [89, 85, 86, 80, 85, 77, 99, 90, 84, 71, None, 89, None, 81, None, 88, None, 78, None, 88, None, 83, None, 101, None]

        with self.db_conn.trans() as trans:
            exact_data = trans.get_data('select * from observation order by station_id, time')
            self.assertEqual(25, len(exact_data))
            self.assertListEqual(exp_temp, [line['temp'] for line in exact_data])
            self.assertListEqual(exp_wind_dir, [line['wind_dir'] for line in exact_data])
            self.assertListEqual(exp_wind_speed, [line['wind_speed'] for line in exact_data])
            self.assertListEqual(exp_wind_gust, [line['wind_gust'] for line in exact_data])
            self.assertListEqual([None] * 25, [line['temp_road'] for line in exact_data])
            self.assertListEqual(exp_rel_hum, [line['rel_hum'] for line in exact_data])
            self.assertListEqual(exp_pressure, [line['pressure'] for line in exact_data])
            self.assertListEqual(exp_station_id, [line['station_id'] for line in exact_data])
            self.assertListEqual([ts_0, ts_1, ts_2] * 3 + [ts_0, ts_3, ts_1, ts_4, ts_2, ts_5] + [ts_1, ts_4, ts_2, ts_5] + [ts_0, ts_3, ts_1, ts_4, ts_2, ts_5], [line['time'] for line in exact_data])


class ImportLandsvirkjunFilesTest(TestCase):

    def setUp(self):
        self.db_conn = make_WHConnection()
        provider = {'ref': 'lv.is', 'name': 'Landsvirkjun'}
        stations = [
            {'ref': 'lv.is.ma.1.02', 'ref_provider': '02m', 'lon': 1, 'lat': 1, 'name': 'Hafið mastur-1 2m'},
            {'ref': 'lv.is.ma.1.57', 'ref_provider': '57m', 'lon': 1, 'lat': 1, 'name': 'Hafið mastur-1 57m'},
            {'ref': 'lv.is.mi.001', 'ref_provider': 'mylla1', 'lon': 1, 'lat': 1, 'name': 'Hafið mylla 1'},
            {'ref': 'lv.is.mi.002', 'ref_provider': 'mylla2', 'lon': 1, 'lat': 1, 'name': 'Hafið mylla 2'}
        ]

        self.inserted_provider_id, self.inserted_stations = setup_database_contents(self.db_conn, provider, stations)

    def tearDown(self):
        teardown_database_contents(self.db_conn, self.inserted_provider_id, self.inserted_stations)

    def test_import_landsvirkjun_meteo_obs(self):
        config_path = os.path.join(project_path, 'test_config.yml')
        test_dir = os.path.join(os.path.dirname(__file__), 'data/landsvirkjun')
        files = []
        for filename in glob.glob(os.path.join(test_dir, 'Haf-mastur*')):
            files.append(filename)

        if not files:
            self.fail('No test files found in %s' % test_dir)
        options = ['--parser', 'LandsvirkjunObservationParser', '--collate', '--config', config_path, '--encoding', 'ISO-8859-1']
        options.extend(files)
        import_files.main(options)

        with self.db_conn.trans() as trans:
            exact_data = trans.get_data('select time::varchar, station_id, temp, wind_dir, wind_speed from observation order by station_id, time')

        expected = [
            ('2013-04-23 10:20:00+00', self.inserted_stations['lv.is.ma.1.02'], None, None, 4.96),
            ('2013-04-23 10:30:00+00', self.inserted_stations['lv.is.ma.1.02'], 0.7, 149.4, 5.15),
            ('2013-04-23 10:40:00+00', self.inserted_stations['lv.is.ma.1.02'], 0.5, 147.1, 4.78),
            ('2013-04-23 10:50:00+00', self.inserted_stations['lv.is.ma.1.02'], 0.7, 136.0, 4.46),
            ('2013-04-23 11:00:00+00', self.inserted_stations['lv.is.ma.1.02'], 0.8, 129.2, 3.43),
            ('2013-04-23 11:10:00+00', self.inserted_stations['lv.is.ma.1.02'], 0.9, 122.1, None),

            ('2013-04-23 10:30:00+00', self.inserted_stations['lv.is.ma.1.57'], -0.3, 136.0, 3.96),
            ('2013-04-23 10:40:00+00', self.inserted_stations['lv.is.ma.1.57'], -0.4, 134.1, 3.83),
            ('2013-04-23 10:50:00+00', self.inserted_stations['lv.is.ma.1.57'], -0.3, 125.9, 3.82),
            ('2013-04-23 11:00:00+00', self.inserted_stations['lv.is.ma.1.57'], -0.1, 123.6, 3.93),
            ('2013-04-23 11:10:00+00', self.inserted_stations['lv.is.ma.1.57'], 0, 119.4, 3.97)
        ]
        self.assertListEqual(expected, exact_data)

    def test_import_landsvirkjun_power_obs(self):
        config_path = os.path.join(project_path, 'test_config.yml')
        test_dir = os.path.join(os.path.dirname(__file__), 'data/landsvirkjun')
        files = []
        for filename in glob.glob(os.path.join(test_dir, 'Haf-vindmyllur*')):
            files.append(filename)

        if not files:
            self.fail('No test files found in %s' % test_dir)
        options = ['--parser', 'LandsvirkjunObservationParser', '--table', 'wind_power', '--config', config_path, '--encoding', 'ISO-8859-1']
        options.extend(files)

        import_files.main(options)

        with self.db_conn.trans() as trans:
            exact_data = trans.get_data('select time::varchar, station_id, power_value from wind_power order by station_id, time')

        expected = [
            ('2013-01-21 12:50:00+00', self.inserted_stations['lv.is.mi.001'], 799.0),
            ('2013-01-21 13:00:00+00', self.inserted_stations['lv.is.mi.001'], 829.0),
            ('2013-01-21 13:10:00+00', self.inserted_stations['lv.is.mi.001'], 761.0),
            ('2013-01-21 13:20:00+00', self.inserted_stations['lv.is.mi.001'], 747.0),
            ('2013-01-21 13:30:00+00', self.inserted_stations['lv.is.mi.001'], 485.0),

            ('2013-01-21 12:50:00+00', self.inserted_stations['lv.is.mi.002'], 0.0),
            ('2013-01-21 13:00:00+00', self.inserted_stations['lv.is.mi.002'], 0.0),
            ('2013-01-21 13:10:00+00', self.inserted_stations['lv.is.mi.002'], 0.0),
            ('2013-01-21 13:20:00+00', self.inserted_stations['lv.is.mi.002'], 0.0),
            ('2013-01-21 13:30:00+00', self.inserted_stations['lv.is.mi.002'], 0.0)
        ]
        self.assertListEqual(expected, exact_data)


class ImportDefaultFilesTest(TestCase):

    def setUp(self):
        self.db_conn = make_WHConnection()
        provider = {'ref': 'one.is', 'name': 'The one'}
        stations = [
            {'ref': 'one.is.1', 'ref_provider': 'one.is.1', 'lon': 1, 'lat': 1, 'name': '1'},
            {'ref': 'one.is.99', 'ref_provider': 'one.is.99', 'lon': 1, 'lat': 1, 'name': '99'},
        ]
        self.inserted_provider_id, self.inserted_stations = setup_database_contents(self.db_conn, provider, stations)

    def tearDown(self):
        teardown_database_contents(self.db_conn, self.inserted_provider_id, self.inserted_stations)

    def test_import_obs(self):
        config_path = os.path.join(project_path, 'test_config.yml')
        test_dir = os.path.join(os.path.dirname(__file__), 'data/basic')
        files = []
        for filename in glob.glob(os.path.join(test_dir, 'basic_*')):
            files.append(filename)

        if not files:
            self.fail('No test files found in %s' % test_dir)
        options = ['--parser', 'CSVWithHeadersObservationParser', '--config', config_path]
        options.extend(files)
        import_files.main(options)

        with self.db_conn.trans() as trans:
            exact_data = trans.get_data('select time::varchar, station_id, temp, wind_speed, rel_hum from observation order by station_id, time')

        expected = [
            ('2000-01-01 00:00:00+00', self.inserted_stations['one.is.1'], 10.1, 1, 81),
            ('2000-01-01 00:10:00+00', self.inserted_stations['one.is.1'], 10.2, 2, 82),
            ('2000-01-01 00:20:00+00', self.inserted_stations['one.is.1'], 10.3, 3, 83),
            ('2000-01-01 00:30:00+00', self.inserted_stations['one.is.1'], 10.4, 4, 84),
            ('2000-01-01 00:40:00+00', self.inserted_stations['one.is.1'], 10.5, 5, 85),
            ('2000-01-01 00:50:00+00', self.inserted_stations['one.is.1'], 10.6, 6, 86),
            ('2000-01-01 00:00:00+00', self.inserted_stations['one.is.99'], 11.1, 11, 91),
            ('2000-01-01 00:10:00+00', self.inserted_stations['one.is.99'], 11.2, 12, 92),
            ('2000-01-01 00:20:00+00', self.inserted_stations['one.is.99'], 11.3, 13, 93),
            ('2000-01-01 00:30:00+00', self.inserted_stations['one.is.99'], 11.4, 14, 94),
            ('2000-01-01 00:40:00+00', self.inserted_stations['one.is.99'], 11.5, 15, 95),
        ]
        self.assertListEqual(expected, exact_data)