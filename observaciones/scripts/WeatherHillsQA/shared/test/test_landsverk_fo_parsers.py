# encoding: utf-8

"""

Tests the ObservationParsers for Landsverk.FO

"""

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime
from nose.tools import assert_dict_equal, assert_false, assert_equal, assert_raises
from parser.landsverk_fo import LandsverkVaisalaObservationParser, LandsverkF34ObservationParser
from util.calculator import round_timestamp_10min
from util.utilities import whLogger

LOG = whLogger(__name__)


def test_landsverk_vaisala_parse_data_line():
    p_v = LandsverkVaisalaObservationParser()
    line_v = '2013 01 01 00:08 3.5 82 0.7 0 1.0 192 NA 4.3 0.00 NA NA 979.4 NA NA NA 1 NA NA NA NA NA NA 0 NA NA' \
             ' 2.0 243 NA NA NA NA 0.0 0.0 NA NA NA NA NA NA NA NA NA NA NA NA NA 0.0 0.0 NA NA NA NA NA NA NA NA NA'
    exp = {
        'time': round_timestamp_10min(datetime(2013, 1, 1, 0, 8, 0)),
        'temp': 3.5,
        'rel_hum': 82.0,
        'wind_speed': 1.0,
        'wind_dir': 192.0,
        'pressure': 979.4,
        'wind_gust': 2.0,
        'temp_road': None
    }
    act = p_v.parse_data_line(line_v)
    LOG.info('act["time"] = %s', act["time"])
    LOG.info('exp["time"] = %s', exp["time"])
    assert_dict_equal(exp, act)


def test_landsverk_vaisala_parse_data_line_error():
    parser = LandsverkVaisalaObservationParser()
    #with assert_raises(IndexError):  STOP now ignores empty lines
    #    parser.parse_data_line('')
    with assert_raises(IndexError):
        parser.parse_data_line('aa\tbb\tccc\tdd')
    with assert_raises(ValueError):
        parser.parse_data_line('a b c d')


def test_landsverk_f34_parse_data_line():
    p_g = LandsverkF34ObservationParser()
    line_g = '2013 10 01 00:08:31 7.5 5.5 9.5 170 160 180 8000 8100 10 2000 NA NA 10.1 9.4 95 1010 997 NA 997.5'
    exp = {
        'time': round_timestamp_10min(datetime(2013, 10, 1, 0, 8, 31)),
        'temp': 10.1,
        'rel_hum': 95.0,
        'wind_speed': 7.5,
        'wind_dir': 170.0,
        'pressure': 997.5,
        'wind_gust': 9.5,
    }
    act = p_g.parse_data_line(line_g)
    assert_dict_equal(exp, act)


def test_landsverk_f34_parse_data_line_error():
    parser = LandsverkF34ObservationParser()
    #with assert_raises(IndexError):  STOP now ignores empty lines
    #    parser.parse_data_line('')
    with assert_raises(IndexError):
        parser.parse_data_line('aa\tbb\tccc\tdd')
    with assert_raises(ValueError):
        parser.parse_data_line('a b c d')


def common_parse_filename(parser):
    parser.parse_file_name('/home/43/13fsfs/2014 F-100/a.phx')
    assert_equal(parser.meta['station_ref'], 'F100')

    parser.parse_file_name('/home/2014 F-30/a.phx')
    assert_equal(parser.meta['station_ref'], 'F30')

    with assert_raises(ValueError):
        parser.parse_file_name('/home/4t3/fafs.xhp')

    with assert_raises(ValueError):
        parser.parse_file_name('fs.fs')


def test_landsverk_vaisala_parse_filename():
    parser = LandsverkVaisalaObservationParser()
    assert_false('station_ref' in parser.meta)
    common_parse_filename(parser)


def test_landsverk_f34_parse_filename():
    parser = LandsverkF34ObservationParser()
    common_parse_filename(parser)


def test_landsverk_vaisala_parse_header_line():
    parser = LandsverkVaisalaObservationParser()
    result = parser.parse_header_line('eyy')
    assert_false(result)


def test_landsverk_f34_parse_header_line():
    parser = LandsverkF34ObservationParser()
    result = parser.parse_header_line('omm')
    assert_false(result)
