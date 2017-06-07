# encoding: utf-8

"""

Parsers for observations from Landsverk in Faroe Islands

"""

from __future__ import absolute_import, division, print_function, unicode_literals
from itertools import chain
import os
import re
from datetime import datetime
from parser import SeparatedTextObservationParser
from util.calculator import round_timestamp_10min
from util.utilities import whLogger


LOG = whLogger(__name__)


def build_date(year, month, day, time):
    parts = (int(s) for s in chain((year, month, day), time.split(':')))
    raw_date = datetime(*parts)
    return round_timestamp_10min(raw_date)


def float_or_na(s):
    if s == 'NA':
        return None
    return float(s)


def parse_file_name(path):
    dirs = path.split(os.sep)[-3:-1]
    found_patterns = []
    for d in dirs:
        found_patterns.extend(re.findall('F-?\d+', d))
    found_patterns = [f.replace('-', '') for f in found_patterns]
    if len(set(found_patterns)) > 1 or not found_patterns:
        LOG.error('Unable to parse file name %s', path)
        raise ValueError('Unable to parse file name %s', path)
    return found_patterns[0]


class LandsverkVaisalaOldObservationParser(SeparatedTextObservationParser):
    def __init__(self):
        super(LandsverkVaisalaOldObservationParser, self).__init__(' ', [
            ('time', build_date, 0, 1, 2, 3),
            ('temp', float_or_na, 4),  # temp 2
            ('rel_hum', float_or_na, 5),  # hum
            ('wind_speed', float_or_na, 8),  # mean1
            ('wind_dir', float_or_na, 9),  # dir
            ('pressure', float_or_na, 12),
            ('wind_gust', float_or_na, 15),  # gust2
        ])
        self.meta['provider_ref'] = 'lv.fo'

    def parse_file_name(self, path):
        self.meta['station_ref'] = parse_file_name(path)


class LandsverkVaisalaObservationParser(SeparatedTextObservationParser):
    def __init__(self):
        super(LandsverkVaisalaObservationParser, self).__init__(' +', [
            ('time', build_date, 0, 1, 2, 3),
            ('temp', float_or_na, 4),  # temp 2
            ('rel_hum', float_or_na, 5),  # hum
            ('wind_speed', float_or_na, 8),  # mean1
            ('wind_dir', float_or_na, 9),  # dir
            ('pressure', float_or_na, 15),
            ('wind_gust', float_or_na, 29),  # gust2
            ('temp_road', float_or_na, 33),  # road1 surface
        ])
        self.meta['provider_ref'] = 'lv.fo'

    def parse_file_name(self, path):
        self.meta['station_ref'] = parse_file_name(path)


class LandsverkF34ObservationParser(SeparatedTextObservationParser):
    def __init__(self):
        super(LandsverkF34ObservationParser, self).__init__(' +', [
            ('time', build_date, 0, 1, 2, 3),
            ('temp', float_or_na, 16),  # temp 2
            ('rel_hum', float_or_na, 18),  # hum
            ('wind_speed', float_or_na, 4),  # mean1
            ('wind_dir', float_or_na, 7),  # dir
            ('pressure', float_or_na, 22),
            ('wind_gust', float_or_na, 6),  # gust2
        ])
        self.meta['provider_ref'] = 'lv.fo'

    def parse_file_name(self, path):
        self.meta['station_ref'] = parse_file_name(path)


class LandsverkF47ObservationParser(SeparatedTextObservationParser):
    def __init__(self):
        super(LandsverkF47ObservationParser, self).__init__(' +', [
            ('time', build_date, 0, 1, 2, 3),
            ('temp', float_or_na, 4),  # TA
            ('rel_hum', float_or_na, 5),  # RH
            ('wind_speed', float_or_na, 13),  # WS
            ('wind_dir', float_or_na, 14),  # WD
            ('pressure', float_or_na, 7),  # PA
            ('wind_gust', float_or_na, 17),  # WSMAX2M
        ])
        self.meta['provider_ref'] = 'lv.fo'

    def parse_file_name(self, path):
        self.meta['station_ref'] = parse_file_name(path)