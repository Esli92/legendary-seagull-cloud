# encoding: utf-8

"""

Utility functions doing calculations.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
from datetime import timedelta, datetime
from time import mktime
from util.utilities import utc


def round_timestamp_10min(dt):
    """Round given timestamp to nearest ten minutes """
    minute = int(round(dt.minute, -1))
    if minute == 60:
        date = datetime(dt.year, dt.month, dt.day, dt.hour, 50, tzinfo=utc) + timedelta(minutes=10)
    else:
        date = datetime(dt.year, dt.month, dt.day, dt.hour, minute, tzinfo=utc)
    return date


def round_timestamp(dt, td):
    if td > timedelta(hours=1):  # and dt.tzinfo is None:
        raise ValueError('Rounding to more than next full hour is not supported.')
    return datetime.fromtimestamp(round(mktime(dt.timetuple()) / td.total_seconds()) * td.total_seconds())


def parse_iso_date(s):

    """ Parse a datetime from string in ISO date format. Only supports GMT/UTC dates """

    s = s.strip()
    FORMATS = ('%Y-%m-%dT%H:%MZ',
               '%Y-%m-%dT%H:%M',
               '%Y-%m-%dT%H:%M:%SZ',
               '%Y-%m-%dT%H:%M:%S',)
    for fmt in FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError as e:
            pass
    raise ValueError('%s is not in a supported date format: %s' % (s, ', '.join(FORMATS)))


def get_forecast_error(measured, forecast, component=None):
    result = abs(measured - forecast)
    if component == 'wind_dir' and result > 180:
        result = 360 - result
    return result


def calc_running_mse(data, history_interval, data_interval):
    """
    :param data:
    :param history_interval: Of how many hours do we want our running mse
    :param data_interval: What interval (hours) does our data have
    """
    timestamps_ordered = sorted(data.keys())
    result = {}
    for t in timestamps_ordered:
        first_for_averaging = t - timedelta(hours=history_interval) + timedelta(hours=data_interval)
        timestamps_for_averaging = [tt for tt in timestamps_ordered if first_for_averaging <= tt <= t]
        mse = (sum(data[tt]**2 for tt in timestamps_for_averaging) / len(timestamps_for_averaging)) ** 0.5
        result[t] = mse
    return result


# Wind related calculations

def get_wind_avg(m):
    s = [np.sin(np.deg2rad(x)) for x in m]
    s = sum(s) / float(len(s))
    c = [np.cos(np.deg2rad(x)) for x in m]
    c = sum(c) / float(len(c))
    value = np.rad2deg(np.arctan2(s, c))
    if value < 0:
        value += 360
    return value


def get_wind_speed(u, v):
    return (u ** 2 + v ** 2) ** 0.5


def get_wind_dir(u, v, point_id, db_conn):
    sql = 'select sinalpha, cosalpha from alpha where point_id=:id'
    with db_conn.trans() as trans:
        alpha = trans.get_data(sql, id=point_id)
    sinalpha = alpha[0]['sinalpha']
    cosalpha = alpha[0]['cosalpha']

    u_true = cosalpha * u + sinalpha * v
    v_true = -sinalpha * u + cosalpha * v

    return np.mod(270 - (np.arctan2(v_true, u_true) * 180 / 3.14159), 360)


