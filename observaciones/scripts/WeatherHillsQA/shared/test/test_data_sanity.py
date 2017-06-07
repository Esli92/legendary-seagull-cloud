from util.data_sanity import check_data_sanity
from nose.tools import assert_list_equal, assert_raises


def test_check_data_sanity():
    ents = [
        {'wind_speed': 2, 'wind_dir': 500},
        {'wind_speed': 2, 'wind_dir': 300},
        {'wind_speed': -2, 'wind_dir': 100},
    ]

    check_data_sanity(ents, False)
    assert_list_equal(ents, [
        {'wind_speed': 2, 'wind_dir': None},
        {'wind_speed': 2, 'wind_dir': 300},
        {'wind_speed': None, 'wind_dir': 100},
    ])

    with assert_raises(ValueError):
        check_data_sanity([{'wind_speed': -10}])

    with assert_raises(ValueError):
        check_data_sanity([{'wind_dir': 360.001}])

    with assert_raises(ValueError):
        check_data_sanity([{'rel_hum': -9999}])

    with assert_raises(ValueError):
        check_data_sanity([{'temp': -273.5}])