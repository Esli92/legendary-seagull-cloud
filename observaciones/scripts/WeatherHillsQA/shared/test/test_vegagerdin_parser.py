from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime
from nose.tools import assert_dict_equal, assert_false, assert_true, assert_equal, assert_raises
from parser.vegagerdin import *
from util.calculator import round_timestamp_10min
from util.utilities import whLogger

LOG = whLogger(__name__)


def test_build_date_tmstamp():
    assert_equal(datetime(2013, 04, 26, 12, 10), build_date_TMSTAMP('2013-04-26 12:10:00'))


def test_build_date_parts():
    assert_equal(datetime(2013, 01, 13, 12), build_date_multipart('1200', '13', '2013'))
    assert_equal(datetime(2012, 12, 31), build_date_multipart('0', '366', '2012'))
    assert_equal(datetime(2013, 12, 31, 0, 50), build_date_multipart('50', '365', '2013'))


def test_parse_header_line():
    parser = VegagerdinObservationParser()
    assert_true(parser.parse_header_line('"TOACI1","v_Braedratunguvegur_093","Main"'))
    assert_true(parser.parse_header_line('"TMSTAMP","RECNBR","volt","f","f_v","d","dsdev","fg","2fg","3fg","t1"'))
    assert_false(parser.parse_header_line('"2013-04-26 12:10:00",57541,13.48,2.518,2.039,25.1,35.33,43.81,9.59,6'))


def test_parse_data_line():
    parser = VegagerdinObservationParser()
    parser.parse_header_line('"TOACI1","v_Braedratunguvegur_093","Main"')
    parser.parse_header_line('"TMSTAMP","RECNBR","volt","f","f_v","d","dsdev","fg","2fg","3fg","t1","t2","rh","tv","bilar1"')
    parsed_line_1 = parser.parse_data_line('"2013-04-26 12:10:00",57541,13.48,2.518,2.039,25.1,35.33,4.116,4.116,4.051,0.853,1.249,43.81,9.59,6')
    expected_1 = {'time': datetime(2013, 4, 26, 12, 10),
                'wind_speed': 2.518,
                'wind_dir': 25.1,
                'wind_gust': 4.116,
                'temp': 0.853,
                'temp_road': 9.59,
                'rel_hum': 43.81}
    assert_dict_equal(expected_1, parsed_line_1)

    parser.parse_header_line('"idstod","t1","rh10","bilar1","tv","f","d","volt","yyyy","doy","hhmm","n/a","n/a","n/a","fg","n/a","n/a","n/a","n/a","n/a","n/a","n/a","n/a","n/a","n/a","tyfir1","n/a","l1"')
    parsed_line_2 = parser.parse_data_line('206,1.187,437.6,18,12.51,3.073,9.44,13.43,2013,116,1220,0,3.922,-6999,5.194,0,0,0,0,0,1.005,18,0,5.194,154.4,3.928,-6999,2.09')
    expected_2 = {'time': datetime(2013, 4, 26, 12, 20),
                  'wind_speed': 3.073,
                  'wind_dir': 9.44,
                  'wind_gust': 5.194,
                  'temp': 1.187,
                  'temp_road': 12.51,
                  'rel_hum': 437.6 / 10}
    assert_dict_equal(expected_2, parsed_line_2)


def test_parse_sequence():
    parser = VegagerdinObservationParser()
    lines = """"TOACI1","vedurstod_060","Main"
"idstod","t1","rh10","bilar1","tv","f","d","volt","yyyy","doy","hhmm","n/a","n/a","n/a","fg","n/a","n/a","n/a","n/a","n/a","n/a","n/a","n/a","n/a","n/a","tyfir1","n/a","l1"
206,1.187,437.6,18,12.51,3.073,9.44,13.43,2013,116,1220,0,3.922,-6999,5.194,0,0,0,0,0,1.005,18,0,5.194,154.4,3.928,-6999,2.09
"""
    data = parser.parse_sequence(lines.splitlines())

    assert_equal(data, [{'time': datetime(2013, 4, 26, 12, 20),
                             'wind_speed': 3.073,
                             'wind_dir': 9.44,
                             'wind_gust': 5.194,
                             'temp': 1.187,
                             'temp_road': 12.51,
                             'rel_hum': 437.6 / 10}])
    meta = parser.get_metadata()
    assert_dict_equal(meta, {'provider_ref': 'vg.is', 'station_ref': '60'})


    lines = """""TOACI1","v_Braedratunguvegur_093","Main"
"TMSTAMP","RECNBR","volt","f","f_v","d","dsdev","fg","2fg","3fg","t1","t2","rh","tv","bilar1"
"2013-04-26 12:10:00",57541,13.48,2.518,2.039,25.1,35.33,4.116,4.116,4.051,0.853,1.249,43.81,9.59,6"""
    data = parser.parse_sequence(lines.splitlines())

    assert_equal(data, [{'time': datetime(2013, 4, 26, 12, 10),
                'wind_speed': 2.518,
                'wind_dir': 25.1,
                'wind_gust': 4.116,
                'temp': 0.853,
                'temp_road': 9.59,
                'rel_hum': 43.81}])
    meta = parser.get_metadata()
    assert_dict_equal(meta, {'provider_ref': 'vg.is', 'station_ref': '93'})
