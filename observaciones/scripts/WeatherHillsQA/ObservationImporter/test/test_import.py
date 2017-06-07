from __future__ import absolute_import, division, print_function, unicode_literals
from nose.tools import assert_equal, assert_true, assert_false, assert_list_equal, assert_items_equal
from mock import MagicMock, call
from import_files import add_station_id, parse_args, merge, remove_empty_entries


def test_add_station_id():
    sf = MagicMock()
    sf.get_station_id.return_value = 30

    obs = [
        {'wind': 10, 'rain': 5, 'fog': 3, 'snow': 0},
        {'wind': 11, 'rain': 6, 'fog': 4, 'snow': 1},
        {'wind': 12, 'rain': 7, 'fog': 5, 'snow': 2},
        {'wind': 13, 'rain': 8, 'fog': 6, 'snow': 3}
    ]

    meta = {'station_ref': 'abc', 'provider_ref': 'def'}

    new_obs = add_station_id(obs, meta, sf)

    sf.get_station_id.assert_called_once_with(ref_provider='abc', provider_ref='def')
    exp_obs = [
        {'wind': 10, 'rain': 5, 'fog': 3, 'snow': 0, 'station_id': 30},
        {'wind': 11, 'rain': 6, 'fog': 4, 'snow': 1, 'station_id': 30},
        {'wind': 12, 'rain': 7, 'fog': 5, 'snow': 2, 'station_id': 30},
        {'wind': 13, 'rain': 8, 'fog': 6, 'snow': 3, 'station_id': 30}
    ]
    assert_equal(exp_obs, new_obs)

    obs = [
        {'wind': 10, 'rain': 5, 'fog': 3, 'snow': 0, 'station_ref': '168'},
        {'wind': 11, 'rain': 6, 'fog': 4, 'snow': 1, 'station_ref': '168'},
        {'wind': 12, 'rain': 7, 'fog': 5, 'snow': 2, 'station_ref': '100'},
        {'wind': 13, 'rain': 8, 'fog': 6, 'snow': 3, 'station_ref': '99'}
    ]
    meta = {'provider_ref': 'abc'}
    sf = MagicMock()
    add_station_id(obs, meta, sf)

    calls = [call.get_station_id(provider_ref=u'abc', ref_provider=u'168'),
             call.get_station_id(provider_ref=u'abc', ref_provider=u'100'),
             call.get_station_id(provider_ref=u'abc', ref_provider=u'99')]

    assert_items_equal(calls, sf.method_calls)


def test_sanity_cli_argument():
    args = parse_args(['--parser', 'LandsverkVaisalaObservationParser', '--config', 'none.txt', '-n', 'ghost.txt'])
    assert_true(args.sanity_null_replace)
    args = parse_args(['--parser', 'LandsverkVaisalaObservationParser', '--config', 'none.txt', 'ghost.txt', '--sanity-null-replace'])
    assert_true(args.sanity_null_replace)
    args = parse_args(['--parser', 'LandsverkVaisalaObservationParser', '--config', 'none.txt', 'ghost.txt'])
    assert_false(args.sanity_null_replace)


def test_merge():
    data_before_merge = [
        {'time': '100', 'station_id': 1, 'temp': 45},
        {'time': '100', 'station_id': 1, 'wind_dir': 200},
        {'time': '200', 'station_id': 1, 'temp': 44},
        {'time': '300', 'station_id': 3, 'temp': 38},
        {'time': '300', 'station_id': 3, 'wind_dir': 300, 'wind_speed': 7},
    ]
    expected = [
        {'time': '100', 'station_id': 1, 'temp': 45, 'wind_dir': 200},
        {'time': '200', 'station_id': 1, 'temp': 44},
        {'time': '300', 'station_id': 3, 'temp': 38, 'wind_dir': 300, 'wind_speed': 7}
    ]
    assert_list_equal(expected, merge(data_before_merge))
#    assert_list_equal(expected, sorted(data_after_merge, key=lambda x: (x['station_id'], x['time'])))


def test_remove_empty_entries():
    data = [
        {'time': '100', 'station_id': 1, 'temp': 45, 'wind_dir': 200},
        {'time': '200', 'station_id': 1, 'temp': None},
        {'time': '300', 'station_id': 3, 'temp': None, 'wind_dir': 300, 'wind_speed': 7},
        {'time': '400', 'station_id': 3, 'temp': None, 'wind_dir': None, 'wind_speed': None}
    ]
    expected = [
        {'time': '100', 'station_id': 1, 'temp': 45, 'wind_dir': 200},
        {'time': '300', 'station_id': 3, 'temp': None, 'wind_dir': 300, 'wind_speed': 7},
    ]
    assert_list_equal(expected, remove_empty_entries(data))


