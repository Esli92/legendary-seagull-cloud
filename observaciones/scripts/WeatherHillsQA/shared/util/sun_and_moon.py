# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta
from math import cos, sin, acos, asin, tan, degrees, radians


# based on: http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html
# also: http://michelanders.blogspot.com/2010/12/calulating-sunrise-and-sunset-in-python.html?showComment=1391011334384#c8082598790102335030

def get_sunrise_sunset(lat, lon, date, offset=0):

    """

    Calculate sunrise and sunset time based on the date, longitude and latitude.
    Offset is the difference from UTC if a different timezone is used.

    """

    localtime = 12.00
    d = (date.replace(tzinfo=None) - datetime(1900, 1, 1)).days + 2

    f = d + 2415018.5 + localtime / 24 - offset / 24
    g = (f - 2451545) / 36525
    q = 23 + (26 + ((21.448 - g * (46.815 + g * (0.00059 - g * 0.001813)))) / 60) / 60
    r = q + 0.00256 * cos(radians(125.04 - 1934.136 * g))
    j = 357.52911 + g * (35999.05029 - 0.0001537 * g)
    k = 0.016708634 - g * (0.000042037 + 0.0000001267 * g)
    l = sin(radians(j)) * (1.914602 - g * (0.004817 + 0.000014 * g)) + sin(radians(2 * j)) * (0.019993 - 0.000101 * g) + sin(radians(3 * j)) * 0.000289
    i = (280.46646 + g * (36000.76983 + g * 0.0003032)) % 360
    m = i + l
    p = m - 0.00569 - 0.00478 * sin(radians(125.04 - 1934.136 * g))
    t = degrees(asin(sin(radians(r)) * sin(radians(p))))
    u = tan(radians(r / 2)) * tan(radians(r / 2))
    v = 4 * degrees(u * sin(2 * radians(i)) - 2 * k * sin(radians(j)) + 4 * k * u * sin(radians(j)) * cos(2 * radians(i)) - 0.5 * u * u * sin(4 * radians(i)) - 1.25 * k * k * sin(2 * radians(j)))
    w = degrees(acos(cos(radians(90.833)) / (cos(radians(lat)) * cos(radians(t))) - tan(radians(lat)) * tan(radians(t))))
    x = (720 - 4 * lon - v + offset * 60) / 1440
    y = (x * 1440 - w * 4) / 1440
    z = (x * 1440 + w * 4) / 1440
    sunrise = y * 24
    sunset = z * 24
    rise_date = datetime(date.year, date.month, date.day, tzinfo=date.tzinfo) + timedelta(hours=sunrise)
    set_date = datetime(date.year, date.month, date.day, tzinfo=date.tzinfo) + timedelta(hours=sunset)
    return rise_date, set_date


# According to Wikipedia, this approximation should be enough for our needs (presenting a weather pictogram with appropriate moon phase)

def get_moon_phase(date):

    """ Get moon phase as a number from range 0-1, 0 and 1 - new moon, 0.25 - first quarter, 0.5 - full moon etc. """

    date = date.replace(tzinfo=None)
    known_new_moon_utc = datetime(2015, 1, 20, 13, 15)
    cycle_total_seconds = timedelta(days=29.530588853).total_seconds()
    moment = (date - known_new_moon_utc).total_seconds() % cycle_total_seconds
    return moment / cycle_total_seconds

