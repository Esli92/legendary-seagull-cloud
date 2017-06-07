# encoding: utf-8

"""

Tests the SeparatedTextObservationParser and simple sub-classes

"""

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime

from nose.tools import assert_false, assert_dict_equal, assert_is_none, assert_true, assert_equal, assert_list_equal, assert_raises, assert_equals

from parser import SeparatedTextObservationParser, InsufficientHeaders
from parser.belgingur import BelgingurObservationParser
from util.calculator import parse_iso_date
from util.utilities import whLogger


LOG = whLogger(__name__)


def test_simple():
    p = SeparatedTextObservationParser(' +', [
        ('smu', str, 0),
        ('foo', str, 2),
        ('bar', str, 5)
    ])

    r = p.parse_header_line('abba   bar   ceres   denali  eifel falaffel giraffe hotel')
    assert_false(r)

    r = p.parse_data_line('Abba   bar   Ceres   denali  eiffel falaffel giraffe hotel')
    assert_dict_equal(r, {'smu': 'Abba', 'foo': 'Ceres', 'bar': 'falaffel'})

    r = p.parse_data_line('Aragorn   Bilbo  Celeborn   Dáin  Éowyn Faramir Gandalf  Háma')
    assert_dict_equal(r, {'smu': 'Aragorn', 'foo': 'Celeborn', 'bar': 'Faramir'})

    r = p.end_input()
    assert_is_none(r)


def test_header_lines():
    p = SeparatedTextObservationParser(' +', [
        ('smu', str, 0),
        ('foo', str, 2),
        ('bar', str, 5)
    ], '^#.*')

    r = p.parse_header_line('# this is a header')
    assert_true(r)

    r = p.parse_header_line('# this is another header')
    assert_true(r)

    r = p.parse_header_line('this is not a header')
    assert_false(r)


def concatenate(*s):
    LOG.info('concatenate: %s', s)
    return ''.join(s)


def build_date(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    year, month, day, hour, minute, second, microsecond = (int(s) for s in (year, month, day, hour, minute, second, microsecond))
    return datetime(year, month, day, hour, minute, second, microsecond)


def test_composite():
    p = SeparatedTextObservationParser(' +', [
        ('timestamp', build_date, 2, 3, 4, 5, 6),
        ('foo', concatenate, 0, 1),
        ('bar', unicode, 7),
    ])

    r = p.parse_header_line('ice cream 2014 04 16 9 48 Bravó')
    assert_false(r)

    r = p.parse_data_line('ice cream 2014 04 16 9 48 Bravó')
    assert_dict_equal(r, {
        'timestamp': datetime(2014, 4, 16, 9, 48),
        'foo': 'icecream',
        'bar': 'Bravó'
    })

    r = p.parse_data_line('lazy boy 1975 3 1 2 31 Sirkus')
    assert_dict_equal(r, {
        'timestamp': datetime(1975, 3, 1, 2, 31),
        'foo': 'lazyboy',
        'bar': 'Sirkus'
    })

    r = p.end_input()
    assert_is_none(r)


def float_or_na(s):
    if s == 'NA':
        return None
    return float(s)


def test_composite_maybe_none():
    p = SeparatedTextObservationParser(' +', [
        ('a_float', float, 2),
        ('maybe_none', float_or_na, 1),
        ('bar', unicode, 3),
    ])
    r = p.parse_data_line('NA 3 3 3 NA')
    assert_dict_equal(r, {
        'a_float': 3.0,
        'maybe_none': 3.0,
        'bar': '3'
    })
    r = p.parse_data_line('NA NA 3 3 NA')
    assert_dict_equal(r, {
        'a_float': 3.0,
        'maybe_none': None,
        'bar': '3'
    })




INPUT_CSV = """
##creation_date=2014-04-21T12:18:34
##created_by=Test Operator, Third Class
#start_date, time, point.id,wind_speed,wind_dir,density,temp,temp_2m
2014-04-16T00:00Z, 2014-04-16T00:00Z, 1,  7.9, 242, 1.2275, -2.3, -1.7
2014-04-16T00:00Z, 2014-04-16T00:10Z, 1,  7.5, 245, 1.2269, -2.3, -1.7
2014-04-16T00:00Z, 2014-04-16T00:20Z, 1,  8.7, 212, 1.2243, -1.8, -1.3
2014-04-16T00:00Z, 2014-04-16T00:30Z, 1, 10.7, 212, 1.2243, -1.8, -1.2
2014-04-16T00:00Z, 2014-04-16T00:40Z, 1, 11.7, 218, 1.2252, -2.0, -1.3
2014-04-16T00:00Z, 2014-04-16T00:50Z, 1, 14.7, 226, 1.2246, -1.8, -1.1
2014-04-16T00:00Z, 2014-04-16T01:00Z, 1, 11.9, 222, 1.2247, -1.8, -1.2
2014-04-16T00:00Z, 2014-04-16T01:10Z, 1, 11.2, 219, 1.2250, -1.9, -1.3
2014-04-16T00:00Z, 2014-04-16T01:20Z, 1, 10.7, 229, 1.2261, -2.1, -1.5
""".split('\n')

INPUT_SSV = [l.replace(',', '  ') for l in INPUT_CSV]


def test_parse_sequence():
    parser = SeparatedTextObservationParser(separator=' *, *', headers='^#.*', field_list=[
        ('timestamp', parse_iso_date, 1),
        ('wind_speed', float, 3),
        ('wind_dir', float, 4),
        ('temp', float, 6),
    ])
    observations = parser.parse_sequence(INPUT_CSV)

    assert_equal(len(observations), 9)
    assert_dict_equal(observations[0], dict(
        timestamp=datetime(2014, 4, 16, 0, 0, 0),
        wind_speed=7.9,
        wind_dir=242,
        temp=-2.3
    ))
    assert_dict_equal(observations[8], dict(
        timestamp=datetime(2014, 4, 16, 1, 20, 0),
        wind_speed=10.7,
        wind_dir=229,
        temp=-2.1
    ))


def test_belgingur_parser_create():
    parser = BelgingurObservationParser()
    assert_equal(parser.separator.pattern, '\s*[,\s]\s*')
    assert_equal(parser.field_list, [])


def test_belgingur_parser_parse_header():
    parser = BelgingurObservationParser()
    header_lines = 0
    for line in INPUT_CSV:
        if not parser.parse_header_line(line):
            break
        header_lines += 1

    assert_equal(header_lines, 4)  # including empty line at beginning
    assert_equal(parser.meta.get('creation_date'), '2014-04-21T12:18:34')
    assert_equal(parser.meta.get('created_by'), 'Test Operator, Third Class')
    field_names = [field[0] for field in parser.field_list]
    assert_list_equal(field_names, [
        'start_date',
        'time',
        'point_id',   # renamed from 'point.id'
        'wind_speed',
        'wind_dir',
        'density',
        'temp',
        'temp_2m'
    ])


def test_pick_converter():
    parser = BelgingurObservationParser()
    assert_equals(parser.pick_converter('something random'), str)
    assert_equals(parser.pick_converter('time'), parse_iso_date)
    assert_equals(parser.pick_converter('wind_speed'), float)
    assert_equals(parser.pick_converter('wind_dir'), float)
    assert_equals(parser.pick_converter('wind_gust'), float)
    assert_equals(parser.pick_converter('temp'), float)
    assert_equals(parser.pick_converter('temp_road'), float)
    assert_equals(parser.pick_converter('temp_ground'), float)


def test_belgingur_two_field_lists():
    parser = BelgingurObservationParser()
    with assert_raises(Exception):
        parser.parse_header_line('#timestamp, foo')
        parser.parse_header_line('#smu  bleh')


def test_belgingur_no_field_list():
    parser = BelgingurObservationParser()
    parser.parse_header_line('##smu=bleh')
    with assert_raises(InsufficientHeaders):
        parser.parse_header_line('foo, bar, baz')


def test_belgingur_parser_parse_data():
    parser = BelgingurObservationParser()
    observations = parser.parse_sequence(INPUT_CSV)

    assert_equal(len(observations), 9)
    assert_dict_equal(observations[0], dict(
        start_date='2014-04-16T00:00Z',
        time=datetime(2014, 4, 16, 0, 0, 0),
        point_id='1',
        wind_speed=7.9,
        wind_dir=242,
        density='1.2275',
        temp=-2.3,
        temp_2m='-1.7',
    ))
    assert_dict_equal(observations[8], dict(
        start_date='2014-04-16T00:00Z',
        time=datetime(2014, 4, 16, 1, 20, 0),
        point_id='1',
        wind_speed=10.7,
        density='1.2261',
        wind_dir=229,
        temp=-2.1,
        temp_2m='-1.5',
    ))
