# encoding: utf-8

"""

Tests the default observation parser

"""

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime
from nose.tools import assert_dict_equal, assert_false, assert_raises, assert_true
from parser.basic import CSVWithHeadersObservationParser, InsufficientHeaders
from util.utilities import whLogger

LOG = whLogger(__name__)


def test_parse_header_line():
    p = CSVWithHeadersObservationParser()
    assert_true(p.parse_header_line('# provider_ref: vi.is'))
    assert_true(p.parse_header_line('# station_ref: vi.is.10'))
    assert_true(p.parse_header_line('time, temp, wind_speed, rh'))
    assert_true(p.parse_header_line('# key: value'))
    assert_true(p.parse_header_line("# 'key': 'value'"))
    assert_false(p.parse_header_line('1,3,4,5'))
    assert_false(p.parse_header_line('vi.is.10,1,3,4,5'))

    p = CSVWithHeadersObservationParser()
    assert_true(p.parse_header_line('# station_ref: vi.is.10'))
    assert_true(p.parse_header_line('# provider_ref: vi.is'))
    assert_true(p.parse_header_line('time, temp, wind_speed, rh'))
    p = CSVWithHeadersObservationParser()

    with assert_raises(InsufficientHeaders):
        p.parse_header_line('time, temp, wind_speed, rh')
        p.parse_header_line('station_ref, time, temp, wind_speed, rh')
        p.parse_header_line('provider_ref, time, temp, wind_speed, rh')


def test_parse_data_line():
    p = CSVWithHeadersObservationParser()
    p.meta['provider_ref'] = 'def.ault'
    p.meta['station_ref'] = 'vi.is.10'
    p.parse_header_line('time, temp, wind_speed, rel_hum')
    line = p.parse_data_line('2014-03-03T00:00:00,23.1,23,80')
    expected = {
        'time': datetime(2014, 3, 3),
        'temp': 23.1,
        'wind_speed': 23,
        'rel_hum': 80
    }
    assert_dict_equal(expected, line)
    line = p.parse_data_line('2014-03-03T00:00:00,23.1,23,-9999')
    expected = {
        'time': datetime(2014, 3, 3),
        'temp': 23.1,
        'wind_speed': 23,
        'rel_hum': None
    }
    assert_dict_equal(expected, line)
    p.parse_header_line('time, temp, wind_speed, rh')
    line = p.parse_data_line('2014-03-03T00:00:00,23.1,23,90')
    expected = {
        'time': datetime(2014, 3, 3),
        'temp': 23.1,
        'wind_speed': 23
    }
    assert_dict_equal(expected, line)

    with assert_raises(ValueError):
        p.parse_data_line('2014-03-03_00:00:00,23.1,23,90')
        p.parse_data_line('2014-03-03T00:00:00,abcd,23,90')
