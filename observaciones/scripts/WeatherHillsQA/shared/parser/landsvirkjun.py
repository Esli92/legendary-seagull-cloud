# encoding: utf-8

"""

Parser for Landsvirkjun data

"""

from __future__ import absolute_import, division, print_function, unicode_literals
import re
import os
from datetime import datetime
from parser import SeparatedTextObservationParser, InsufficientHeaders
from util.calculator import parse_iso_date, round_timestamp_10min
from util.utilities import whLogger

FIELD_ALIASES_WIND_DATA = {
    'WDir': 'wind_dir',
    'WSpeed': 'wind_speed',
    'AT': 'temp',
    'Pw': 'power_value'
}

FIELD_ALIASES_CSV = {
    'F': 'wind_speed',
    'FG': 'wind_gust',
    'D': 'wind_dir',
    'T': 'temp',
    'P': 'pressure',
    'RH': 'rel_hum'
}


def build_date_landsvirkjun(date, time):
    return round_timestamp_10min(datetime.strptime(date + time, '%d.%m.%Y%H:%M:%S'))


def parse_time_csv(s):##2010-09-03_00:00:00.0
    return datetime.strptime(s, '%Y-%m-%d_%H:%M:%S.0')


def float_or_no_data(s):
    if s in ['---', '7999.0', '3533.0', '-9999.0']:
        return None
    return float(s)


class LandsvirkjunObservationParser(SeparatedTextObservationParser):

    def __init__(self):
        # headers = '^([^:]+:[^:]+|Date,Time,Value.*,State of value)$'  # either `key: value` pairs or actual header text
        headers = '^[^:]+:[^:]+$|Date,Time,Value.*,State of value.*$'  # either `key: value` pairs or actual header text
        super(LandsvirkjunObservationParser, self).__init__(',', headers=headers)
        self.meta['provider_ref'] = 'lv.is'
        # Do we actually want those headers content to be stored in self.meta?

    def parse_file_name(self, path):
        #pattern = '^Haf-mastur_(.+)_([0-9]+m)(-monitor[12])?_[0-9]+\..+'
        pattern = '^Haf-(mastur|vindmyllur)_(.+)_([0-9]+m|Mylla[12])(-monitor[12])?_[0-9]+\..+'
        try:
            #component, self.meta['station_ref'] = re.match(pattern, os.path.basename(path)).groups()[:2]
            component, station_ref = re.match(pattern, os.path.basename(path)).groups()[1:3]
            self.meta['station_ref'] = station_ref.lower()
            self.field_list = [('time', build_date_landsvirkjun, 0, 1), (FIELD_ALIASES_WIND_DATA[component], float_or_no_data, 2)]
        except (AttributeError, KeyError):
            raise ValueError('Improper file name')


class LandsvirkjunCsvObservationParser(SeparatedTextObservationParser):

    """ Parse Landsvirkjun data from csv files, originating (I guess) from some Belgingur database. """

    def __init__(self):
        super(LandsvirkjunCsvObservationParser, self).__init__(separator=',', headers='[A-Z]*[,A-Z]+[A-Z]*')
        self.meta['provider_ref'] = 'lv.is'

    def parse_header_line(self, line):
        if not super(LandsvirkjunCsvObservationParser, self).parse_header_line(line):
            return False
        if line != '':
            parts = self.separator.split(line.strip())
            self.field_list = [('time', parse_time_csv, parts.index('TIMI')), ('station_ref', str, parts.index('STOD'))]
            for key_in, key_out in FIELD_ALIASES_CSV.iteritems():
                if key_in in parts:
                    self.field_list.append((key_out, float_or_no_data, parts.index(key_in)))
        return True
