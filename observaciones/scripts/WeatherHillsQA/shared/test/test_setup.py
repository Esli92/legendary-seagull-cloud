from __future__ import absolute_import, division, print_function, unicode_literals
from nose.tools import assert_equal, assert_true
from setup_landsverk_fo import read_landsverk_stations
from setup_vegagerdin_is import read_vegagerdin_stations


def test_read_landsverk_csv():
    stations = read_landsverk_stations()
    assert_equal(31, len(stations))
    for station in stations:
        assert_equal(station['ref_provider'][1:], station['ref'][6:])


def test_read_vegagerdin_csv():
    stations = read_vegagerdin_stations()
    assert_equal(86, len(stations))
    for station in stations:
        assert_equal(sorted(station.keys()), ['has', 'lat', 'lon', 'name', 'ref', 'ref_provider', 'ref_wmo'])
        assert_true(-25.0 < station['lon'] < -13.0)
        assert_true(63.0 < station['lat'] < 67.0)
        assert_true(0 < station['has'] < 620.0 or station['has'] is None)

