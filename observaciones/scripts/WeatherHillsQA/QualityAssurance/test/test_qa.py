# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals


from nose.tools import assert_list_equal, assert_dict_equal, assert_equal
from datetime import datetime, timedelta, date
from random import sample
from collections import defaultdict
from qa import ts_by_day, slice_data, result_dict_to_entries, get_data_steps, collect_days_to_assess


def test_ts_by_day():

    ts1 = datetime(2015, 6, 10)
    ts_set = {ts1 + timedelta(hours=i) for i in range(48)}

    add = [[], [datetime(2015, 6, 10, 23)]]
    days = [[ts1 + timedelta(hours=i) for i in range(24)], [add[1][0] + timedelta(hours=i) for i in range(25)]]

    a = []
    d = []
    for t, p in ts_by_day(ts_set, [ts1.date(), (ts1 + timedelta(hours=24)).date()], timedelta(hours=1)):
        a.append(p)
        d.append(t)
    assert_list_equal(add, sorted(a))
    assert_list_equal(days, sorted(d))

    a2 = []
    d2 = []
    for t, p in ts_by_day(ts_set, [ts1.date()], timedelta(hours=1)):
        a2.append(p)
        d2.append(t)

    assert_list_equal(add[:1], sorted(a2))
    assert_list_equal(days[:1], sorted(d2))

    hours = [0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 15, 19, 21, 22]

    gapped_ts_set = {ts1 + timedelta(hours=i) for i in hours}
    s_days, s_ts = ts_by_day(gapped_ts_set, [ts1.date()], tolerance=timedelta(hours=1)).next()
    other_hours = [6, 8, 12, 16, 20]
    days_expected = sorted([ts1 + timedelta(hours=i) for i in hours + other_hours])
    ts_expected = sorted([ts1 + timedelta(hours=i) for i in other_hours])
    assert_list_equal(days_expected, s_days)
    assert_list_equal(ts_expected, s_ts)


def test_slice_data():
    ts1 = datetime(2015, 6, 10)
    ts15 = datetime(2015, 6, 10, 7)
    ts_for_slice = [ts15 + timedelta(hours=i) for i in xrange(7)]

    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None))))
    for i in range(72):
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp']['vi.is.1'] = (10 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp']['vi.is.2'] = (20 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp']['vi.is.1'] = (11 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp']['vi.is.2'] = (22 + i, False)

    slice1 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
    slice1['temp']['vi.is.1'] = {ts15 + timedelta(hours=i): 17 + i for i in range(7)}
    slice1['temp']['vi.is.2'] = {ts15 + timedelta(hours=i): 27 + i for i in range(7)}
    slice1['wsp']['vi.is.1'] = {ts15 + timedelta(hours=i): 18 + i for i in range(7)}
    slice1['wsp']['vi.is.2'] = {ts15 + timedelta(hours=i): 29 + i for i in range(7)}

    slice2 = slice_data(ts_for_slice, data, ['vi.is.1', 'vi.is.2'], ['temp', 'wsp'])

    assert_dict_equal(slice1, slice2)

    slice1['temp']['vi.is.1'][ts1 - timedelta(hours=7)] = None
    slice1['temp']['vi.is.2'][ts1 - timedelta(hours=7)] = None
    slice1['wsp']['vi.is.1'][ts1 - timedelta(hours=7)] = None
    slice1['wsp']['vi.is.2'][ts1 - timedelta(hours=7)] = None

    ts_for_slice.append(ts1 - timedelta(hours=7))

    slice2 = slice_data(ts_for_slice, data, ['vi.is.1', 'vi.is.2'], ['temp', 'wsp'])
    assert_dict_equal(slice1, slice2)


def test_result_dict_to_entries():
    ts1 = datetime(2015, 6, 10)
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None))))

    for i in range(72):
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][1] = (10 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][2] = (20 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp'][1] = (11 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp'][2] = (22 + i, False)

    for i in range(70, 72):
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][1] = (10 + i, True)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][2] = (20 + i, True)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp'][2] = (22 + i, True)


    qa = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: list)))
    qa['temp'][1] = {ts1 + timedelta(hours=i): [1, 2, 3, 4] for i in range(72)}
    qa['temp'][2] = {ts1 + timedelta(hours=i): [5, 6, 7, 8] for i in range(72)}
    qa['wsp'][1] = {ts1 + timedelta(hours=i): [8, 7, 6, 5] for i in range(72)}
    qa['wsp'][2] = {ts1 + timedelta(hours=i): [4, 3, 2, 1] for i in range(72)}

    expected = []

    expected.extend([{'time': ts1 + timedelta(hours=i), 'variable': 'temp', 'station_id': 1, 'value': 10 + i, 'q_range': 1, 'q_step': 2, 'q_persistence': 3, 'q_spatial': 4} for i in xrange(70)])
    expected.extend([{'time': ts1 + timedelta(hours=i), 'variable': 'temp', 'station_id': 2, 'value': 20 + i, 'q_range': 5, 'q_step': 6, 'q_persistence': 7, 'q_spatial': 8} for i in xrange(70)])
    expected.extend([{'time': ts1 + timedelta(hours=i), 'variable': 'wsp', 'station_id': 1, 'value': 11 + i, 'q_range': 8, 'q_step': 7, 'q_persistence': 6, 'q_spatial': 5} for i in xrange(72)])
    expected.extend([{'time': ts1 + timedelta(hours=i), 'variable': 'wsp', 'station_id': 2, 'value': 22 + i, 'q_range': 4, 'q_step': 3, 'q_persistence': 2, 'q_spatial': 1} for i in xrange(70)])

    result = result_dict_to_entries(qa, data, [])

    assert_list_equal(sorted(expected), sorted(result))

    # inactive hours and some nodata on the way

    active_hours = sample(range(72), 50)
    inactive_hours = [ts1 + timedelta(hours=i) for i in range(72) if i not in active_hours]

    for i in range(70, 72):
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][1] = (10 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][2] = (20 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp'][2] = (22 + i, False)

    for i in xrange(72):
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][2] = (None, False)

    expected = []

    expected.extend([{'time': ts1 + timedelta(hours=i), 'variable': 'temp', 'station_id': 1, 'value': 10 + i, 'q_range': 1, 'q_step': 2, 'q_persistence': 3, 'q_spatial': 4} for i in active_hours])
    expected.extend([{'time': ts1 + timedelta(hours=i), 'variable': 'wsp', 'station_id': 1, 'value': 11 + i, 'q_range': 8, 'q_step': 7, 'q_persistence': 6, 'q_spatial': 5} for i in active_hours])
    expected.extend([{'time': ts1 + timedelta(hours=i), 'variable': 'wsp', 'station_id': 2, 'value': 22 + i, 'q_range': 4, 'q_step': 3, 'q_persistence': 2, 'q_spatial': 1} for i in active_hours])
    expected.extend([{'time': ts1 + timedelta(hours=i), 'variable': 'temp', 'station_id': 2, 'value': None, 'q_range': 5, 'q_step': 6, 'q_persistence': 7, 'q_spatial': 8} for i in active_hours])

    result = result_dict_to_entries(qa, data, inactive_hours)

    assert_list_equal(sorted(expected), sorted(result))


def test_collect_days_to_assess():

    ts1 = datetime(2015, 1, 1)
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None))))
    for i in range(24) + range(48, 72) + range(96, 125):
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][1] = (10 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][2] = (20 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp'][1] = (11 + i, False)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp'][2] = (22 + i, False)
    for i in range(24, 48):
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][1] = (10 + i, True)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['temp'][2] = (20 + i, True)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp'][1] = (11 + i, True)
        data[(ts1 + timedelta(hours=i)).date()][ts1 + timedelta(hours=i)]['wsp'][2] = (22 + i, True)

    ts_x = datetime(2015, 1, 1, 15)
    ts_y = datetime(2015, 1, 3, 12)

    data[ts_x.date()][ts_x]['temp'][1] = (None, None)
    data[ts_y.date()][ts_y]['temp'][2] = (0, True)

    days = collect_days_to_assess(data)
    expected_days = [date(2015, 1, 1), date(2015, 1, 3), date(2015, 1, 5), date(2015, 1, 6)]

    assert_list_equal(sorted(expected_days), sorted(days))


def test_get_data_steps():
    n_stations = 14
    n_vars = 4
    start = datetime(2014, 1, 1)
    end = datetime(2015, 12, 31, 23, 59, 59)

    steps = get_data_steps(n_stations, n_vars, start, end)
    assert_equal(3, len(steps))

    assert_equal(start, steps[0][0])
    assert_equal(end, steps[-1][1])

    for ((_, e1), (s2, _)) in zip(steps[:-1], steps[1:]):
        assert_equal(e1 + timedelta(seconds=1), s2)

    end = datetime(2014, 1, 10)
    steps = get_data_steps(n_stations, n_vars, start, end)
    assert_equal(1, len(steps))

    assert_equal((start, end), steps[0])

    n_stations = 30
    end = datetime(2015, 12, 31, 23, 59, 59)

    steps = get_data_steps(n_stations, n_vars, start, end)
    assert_equal(5, len(steps))
