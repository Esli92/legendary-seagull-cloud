# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import assert_equal, assert_almost_equal, assert_not_almost_equal, assert_raises
from util.calculator import *


def test_angle_averaging():
    assert_almost_equal(get_wind_avg([300, 60]), 0.0)
    assert_almost_equal(get_wind_avg([100, 120]), 110)
    assert_almost_equal(get_wind_avg([10, 30, 350]), 10)
    assert_almost_equal(get_wind_avg([10, 10, 330, 330]), 350)


def test_angle_subtracting():
        assert_equal(get_forecast_error(350, 10, "wind_dir"), 20)
        assert_equal(get_forecast_error(120, 180, "wind_dir"), 60)
        assert_equal(get_forecast_error(179, 180, "wind_dir"), 1)
        assert_equal(get_forecast_error(181, 1, "wind_dir"), 180)
        assert_equal(get_forecast_error(20, 290, "wind_dir"), 90)


def test_running_mse():
    t1 = datetime(2013, 1, 1, 6)
    x = range(1, 20)
    test = {t1 + timedelta(hours=6*i): v for i, v in enumerate(x)}

    result = calc_running_mse(test, 48, 6)
    keys_sorted = sorted(result.keys())

    assert_almost_equal(result[keys_sorted[-1]] ** 2, sum(i ** 2 for i in range(12, 20)) / 8)
    assert_almost_equal(result[keys_sorted[7]] ** 2, sum(i ** 2 for i in range(1, 9)) / 8)
    assert_almost_equal(result[keys_sorted[5]] ** 2, sum(i ** 2 for i in range(1, 7)) / 6)

    del test[datetime(2013, 1, 1, 12)]
    result = calc_running_mse(test, 48, 6)
    keys_sorted = sorted(result.keys())

    #so it has to take from seven values...
    eighth = sum(i ** 2 for i in [1, 3, 4, 5, 6, 7, 8]) / 7
    wrong_eighth = sum(i ** 2 for i in [1, 3, 4, 5, 6, 7, 8]) / 8
    assert_not_almost_equal(result[keys_sorted[6]] ** 2, wrong_eighth)
    assert_almost_equal(result[keys_sorted[6]] ** 2, eighth)


def test_round_timestamp():
    dt = datetime(2014, 12, 13, 14, 15, 16)
    assert_equal(datetime(2014, 12, 13, 14, 15), round_timestamp(dt, timedelta(minutes=5)))
    assert_equal(datetime(2014, 12, 13, 14, 20), round_timestamp(dt, timedelta(minutes=10)))
    assert_equal(datetime(2014, 12, 13, 14, 15), round_timestamp(dt, timedelta(minutes=15)))
    assert_equal(datetime(2014, 12, 13, 14, 30), round_timestamp(dt, timedelta(minutes=30)))
    assert_equal(datetime(2014, 12, 13, 14), round_timestamp(dt, timedelta(hours=1)))
    #assert_equal(datetime(2014, 12, 13, 14), round_timestamp_minutes(dt, timedelta(hours=2)))
    dt = datetime(2013, 2, 28, 23, 22, 31)
    assert_equal(datetime(2013, 2, 28, 23, 25), round_timestamp(dt, timedelta(minutes=5)))
    assert_equal(datetime(2013, 2, 28, 23, 30), round_timestamp(dt, timedelta(minutes=15)))
    #assert_equal(datetime(2013, 3, 1), round_timestamp_minutes(dt, timedelta(minutes=120)))
    dt = datetime(2013, 5, 31, 21, 32, 31)
    assert_equal(datetime(2013, 5, 31, 22), round_timestamp(dt, timedelta(hours=1)))
    with assert_raises(ValueError):
        round_timestamp(dt, timedelta(hours=2))