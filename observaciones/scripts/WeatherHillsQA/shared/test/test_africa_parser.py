from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import assert_dict_equal, assert_false, assert_raises, assert_true, assert_is_none, assert_equal
from parser.africa import *


line = " FALE      ,10/28/2016,09:14,OTHER-MTR ,           ,   293.149994,    88.425987,100406.796875,   295.149994,   190.000000,     4.100000,   127.000000,   -29.629999,    31.129999,"


def test_parse_header_line():
    parser = MADISObservationParser()
    assert_true(parser.parse_header_line(''))
    assert_false(parser.parse_header_line('some line'))
    assert_false(parser.parse_header_line(line))


def test_parse_data_line():
    parser = MADISObservationParser()

    expected = {
        'station_ref': 'FALE',
        'time': datetime(2016, 10, 28, 9, 14),
        'provider_ref': 'af.mtr',
        'dew': 20,
        'rel_hum': 88.426,
        'pressure': 1004.068,
        'temp': 22,
        'wind_dir': 190.0,
        'wind_speed': 4.1
    }

    assert_dict_equal(expected, parser.parse_data_line(line))


def test_float_or_na():
    assert_is_none(float_or_na(''))
    assert_equal(0.3333, float_or_na('0.333333333333'))
    assert_equal(0.3333, float_or_na(1/3))
    assert_equal(0.3, float_or_na('0.3'))
    assert_equal(124, float_or_na('124'))
    assert_equal(287.15, float_or_na('287.149994'))


def test_parse_date():
    assert_equal(datetime(2016, 10, 28, 9, 14), parse_date('10/28/2016', '09:14'))
    with assert_raises(ValueError):
        parse_date('10/28/2016', '9.14')
    with assert_raises(ValueError):
        parse_date('10-28-2016', '9:14')


def test_parse_temperature():
    assert_equal(0, parse_temperature(273.15))
    assert_equal(13, parse_temperature(286.15))


def test_parse_pressure():
    assert_equal(1013, parse_pressure(101300))
