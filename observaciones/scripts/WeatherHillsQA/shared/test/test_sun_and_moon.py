from nose.tools import assert_less, assert_true
from datetime import datetime

from util.sun_and_moon import get_moon_phase


def test_get_moon_phase():
    assert_true((get_moon_phase(datetime(2015, 4, 18, 18, 58)) < 0.025) != (1 - get_moon_phase(datetime(2015, 4, 18, 18, 58)) < 0.025))
    assert_true((get_moon_phase(datetime(2015, 5, 18, 4, 15)) < 0.025) != (1 - get_moon_phase(datetime(2015, 5, 18, 4, 15)) < 0.025))
    assert_less(abs(get_moon_phase(datetime(2015, 5, 4, 3, 43)) - 0.5), 0.025)
    assert_less(abs(get_moon_phase(datetime(2015, 6, 2, 16, 20)) - 0.5), 0.025)
    assert_less(abs(get_moon_phase(datetime(2015, 4, 12, 3, 46)) - 0.75), 0.025)
    assert_less(abs(get_moon_phase(datetime(2015, 9, 21, 9)) - 0.25), 0.025)
    assert_less(abs(get_moon_phase(datetime(2009, 11, 9, 15, 57)) - 0.75), 0.025)
    assert_less(abs(get_moon_phase(datetime(2009, 10, 26, 0, 43)) - 0.25), 0.025)

