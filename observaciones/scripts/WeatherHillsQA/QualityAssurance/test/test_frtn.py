# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals


from nose.tools import assert_list_equal, assert_dict_equal
from datetime import datetime
from collections import defaultdict


from frtn import make_frtn_input, process_frtn_output


def test_make_frtn_input():
    pass

    expected = [
        '2 3 4',
        'af.1       af.2       af.3      ',
        'temp       wsp        wdir       rh        ',
        '51.5 51.5 52.5 52.5 53.5 53.5',
        '21.5 21.5 22.5 22.5 23.5 23.5',
        '101.5 101.5 102.5 102.5 103.5 103.5',
        '            271.0000            272.0000            281.0000            282.0000            291.0000            292.0000             11.0000             12.0000             21.0000             22.0000             31.0000             32.0000            311.0000            312.0000            321.0000            322.0000            331.0000            332.0000             61.0000             62.0000             71.0000             72.0000             81.0000             82.0000'
    ]
    stations = [
        {'ref': 'af.1', 'lat': 51.5, 'lon': 21.5, 'has': 101.5, 'id': 'af.1'},
        {'ref': 'af.2', 'lat': 52.5, 'lon': 22.5, 'has': 102.5, 'id': 'af.2'},
        {'ref': 'af.3', 'lat': 53.5, 'lon': 23.5, 'has': 103.5, 'id': 'af.3'},
    ]

    ts1 = datetime(2015, 6, 10)
    ts2 = datetime(2015, 6, 11)

    variables = ['temp', 'wind_speed', 'wind_dir', 'rel_hum']
    timestamps = [ts1, ts2]

    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
    data['temp']['af.1'] = {ts1: -2.15, ts2: -1.15}
    data['temp']['af.2'] = {ts1: 7.85, ts2: 8.85}
    data['temp']['af.3'] = {ts1: 17.85, ts2: 18.85}

    data['wind_speed']['af.1'] = {ts1: 11, ts2: 12}
    data['wind_speed']['af.2'] = {ts1: 21, ts2: 22}
    data['wind_speed']['af.3'] = {ts1: 31, ts2: 32}

    data['wind_dir']['af.1'] = {ts1: 311, ts2: 312}
    data['wind_dir']['af.2'] = {ts1: 321, ts2: 322}
    data['wind_dir']['af.3'] = {ts1: 331, ts2: 332}

    data['wind_speed']['af.1'] = {ts1: 11, ts2: 12}
    data['wind_speed']['af.2'] = {ts1: 21, ts2: 22}
    data['wind_speed']['af.3'] = {ts1: 31, ts2: 32}

    data['rel_hum']['af.1'] = {ts1: 61, ts2: 62}
    data['rel_hum']['af.2'] = {ts1: 71, ts2: 72}
    data['rel_hum']['af.3'] = {ts1: 81, ts2: 82}

    result = make_frtn_input(data, stations, variables, timestamps)

    assert_list_equal(expected, result)


def test_process_frtn_output():
    # n_times, n_stations, n_vars, 4)
    # first ts, first station, first var, first test
    # second ts, first station, first var, first test
    # first ts, second station, first var, first test ...

    ts1 = datetime(2015, 6, 10)
    ts2 = datetime(2015, 6, 11)

    variables = ['temp', 'wind_speed', 'wind_dir', 'rel_hum']
    timestamps = [ts1, ts2]
    stations = ['af.1', 'af.2', 'af.3']

    output = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 1.test
              8, 0, 8, 0, 8, 0, 8, 0, 8, 0, 8, 0, 8, 0, 8, 0, 8, 0, 8, 0, 8, 0, 8, 0,  # 2.test
              8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8,  # 3.test
              2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 4.test
    qa = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: list)))

    qa['temp']['af.1'] = {ts1: [0, 8, 8, 2], ts2: [0, 0, 8, 2]}
    qa['temp']['af.2'] = {ts1: [0, 8, 8, 2], ts2: [0, 0, 8, 2]}
    qa['temp']['af.3'] = {ts1: [0, 8, 8, 2], ts2: [0, 0, 8, 2]}

    qa['wind_speed']['af.1'] = {ts1: [0, 8, 8, 1], ts2: [0, 0, 8, 1]}
    qa['wind_speed']['af.2'] = {ts1: [0, 8, 8, 1], ts2: [0, 0, 8, 1]}
    qa['wind_speed']['af.3'] = {ts1: [0, 8, 8, 1], ts2: [0, 0, 8, 1]}

    qa['wind_dir']['af.1'] = {ts1: [0, 8, 8, 0], ts2: [0, 0, 8, 0]}
    qa['wind_dir']['af.2'] = {ts1: [0, 8, 8, 0], ts2: [0, 0, 8, 0]}
    qa['wind_dir']['af.3'] = {ts1: [0, 8, 8, 0], ts2: [0, 0, 8, 0]}

    qa['rel_hum']['af.1'] = {ts1: [0, 8, 8, 0], ts2: [0, 0, 8, 0]}
    qa['rel_hum']['af.2'] = {ts1: [0, 8, 8, 0], ts2: [0, 0, 8, 0]}
    qa['rel_hum']['af.3'] = {ts1: [0, 8, 8, 0], ts2: [0, 0, 8, 0]}

    result = process_frtn_output(output, stations, variables, timestamps)
    assert_dict_equal(qa, result)