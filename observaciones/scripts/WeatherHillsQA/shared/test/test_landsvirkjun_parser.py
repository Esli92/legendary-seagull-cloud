# encoding: utf-8

"""

Tests the ObservationParsers for Landsvirkjun

"""

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime
from nose.tools import assert_dict_equal, assert_false, assert_equal, assert_raises, assert_true, assert_list_equal
from parser.landsvirkjun import LandsvirkjunObservationParser, build_date_landsvirkjun, float_or_no_data
from util.utilities import whLogger, utc

LOG = whLogger(__name__)


def test_parse_header_line():
    parser = LandsvirkjunObservationParser()
    assert_true(parser.parse_header_line("Station Site:	Búrfell"))
    assert_true(parser.parse_header_line("LocalY:	403270.228300"))
    assert_true(parser.parse_header_line("Parameter Type Name:	---"))
    assert_true(parser.parse_header_line("Time series Name:	BUR/201304230000/AT_01/Cmd.O"))
    assert_true(parser.parse_header_line("Time series Unit:	°C"))
    assert_true(parser.parse_header_line("Date,Time,Value [°C],State of value"))
    assert_true(parser.parse_header_line("Date,Time,Value [m/s],State of value"))
    assert_true(parser.parse_header_line("Date,Time,Value [°],State of value"))
    assert_true(parser.parse_header_line("Date,Time,Value [�C],State of value"))
    assert_false(parser.parse_header_line("hey "))
    assert_false(parser.parse_header_line("hey there"))
    assert_false(parser.parse_header_line("23.04.2013,11:10:00,0.9,200 (Unchecked)"))


def test_parse_data_line():
    parser = LandsvirkjunObservationParser()
    parser.parse_file_name("Haf-mastur_AT_02m_20140203.O.csv")

    expected = {
        'time': datetime(2013, 4, 23, 11, 20, tzinfo=utc),
        'temp': 0.7
    }
    actual = parser.parse_data_line("23.04.2013,11:20:00,0.7,200 (Unchecked)")
    assert_dict_equal(expected, actual)
    expected = {
        'time': datetime(2013, 4, 23, 11, 20, tzinfo=utc),
        'temp': None
    }
    actual = parser.parse_data_line("23.04.2013,11:20:00,---,200 (Unchecked)")
    assert_dict_equal(expected, actual)
    parser.parse_file_name("Haf-vindmyllur_Pw_Mylla1_20140203.O.csv")

    expected = {
        'time': datetime(2013, 1, 21, 12, 50, tzinfo=utc),
        'power_value': 799.0
    }
    actual = parser.parse_data_line("21.01.2013,12:50:00,799.00,254")
    assert_dict_equal(expected, actual)


def test_parse_file_name():
    parser = LandsvirkjunObservationParser()

    parser.parse_file_name("Haf-mastur_AT_02m_20140203.O.csv")
    assert_equal(parser.meta['station_ref'], '02m')
    assert_list_equal(parser.field_list, [('time', build_date_landsvirkjun, 0, 1), ('temp', float_or_no_data, 2)])

    parser.parse_file_name("../Haf-mastur_AT_02m_20140203.O.csv")
    assert_equal(parser.meta['station_ref'], '02m')
    assert_list_equal(parser.field_list, [('time', build_date_landsvirkjun, 0, 1), ('temp', float_or_no_data, 2)])

    parser.parse_file_name("/home/karolina/Haf-mastur_AT_02m_20140203.O.csv")
    assert_equal(parser.meta['station_ref'], '02m')
    assert_list_equal(parser.field_list, [('time', build_date_landsvirkjun, 0, 1), ('temp', float_or_no_data, 2)])

    parser.parse_file_name('Haf-mastur_WSpeed_57m-monitor1_20140203.O.csv')
    assert_equal(parser.meta['station_ref'], '57m')
    assert_list_equal(parser.field_list, [('time', build_date_landsvirkjun, 0, 1), ('wind_speed', float_or_no_data, 2)])

    parser.parse_file_name('Haf-vindmyllur_Pw_Mylla1_20140203.O.csv')
    assert_equal(parser.meta['station_ref'], 'mylla1')
    assert_list_equal(parser.field_list, [('time', build_date_landsvirkjun, 0, 1), ('power_value', float_or_no_data, 2)])

    with assert_raises(ValueError):
        parser.parse_file_name('Haf-mastur_WSpeed_StdDev_56m-monitor2_20140203.O.csv')

    with assert_raises(ValueError):
        parser.parse_file_name('nothing.txt')


def test_build_date_landsvirkjun():
    assert_equal(datetime(2013, 4, 23, 10, 40, tzinfo=utc), build_date_landsvirkjun("23.04.2013", "10:40:00"))
    assert_equal(datetime(2013, 4, 23, 10, 40, tzinfo=utc), build_date_landsvirkjun("23.04.2013", "10:44:00"))
    assert_equal(datetime(2013, 4, 23, 10, 40, tzinfo=utc), build_date_landsvirkjun("23.04.2013", "10:38:32"))

