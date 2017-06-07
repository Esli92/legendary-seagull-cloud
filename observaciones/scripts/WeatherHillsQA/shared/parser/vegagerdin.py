# encoding: utf-8

"""

Parsers for observations from Vegagerdin in Iceland

"""


from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime
from parser import SeparatedTextObservationParser
from util.utilities import whLogger


LOG = whLogger(__name__)


def build_date_TMSTAMP(date):
    date = date.strip('"')
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


def build_date_multipart(hhmm, doy, yyyy):
    return datetime.strptime(hhmm.zfill(4) + doy.zfill(3) + yyyy, '%H%M%j%Y')


def float_or_no_data(s):
    if s in ['-7999', '6999', '-6999']:
        return None
    return float(s)


def rh10_float_or_no_data(s):
    if float_or_no_data(s) is not None:
        return float_or_no_data(s) / 10


def parse_column_names(column_list):

    """
    Construct field list to be used by the line parser, taking into account (different) field names in the header line.
    """

    field_list = []

    if 'TMSTAMP' in column_list:
        field_list.append(('time', build_date_TMSTAMP, column_list.index('TMSTAMP')))
    elif all([i in column_list for i in ['hhmm', 'doy', 'yyyy']]):
        field_list.append(('time', build_date_multipart,
                           column_list.index('hhmm'), column_list.index('doy'), column_list.index('yyyy')))
    else:
        raise ValueError('Not enough date parts to understand timestamp')

    # parse relative humidity
    if 'rh' in column_list:
        field_list.append(('rel_hum', float_or_no_data, column_list.index('rh')))
    elif 'rh10' in column_list:
        field_list.append(('rel_hum', rh10_float_or_no_data, column_list.index('rh10')))

    # parse all the rest of values
    common_keys = {
        'd': 'wind_dir',
        'f': 'wind_speed',
        'fg': 'wind_gust',
        't1': 'temp',
        'tv': 'temp_road',
        'ps': 'pressure',
    }
    for key_in, key_out in common_keys.iteritems():
        if key_in in column_list:
            field_list.append((key_out, float_or_no_data, column_list.index(key_in)))
    return field_list


class VegagerdinObservationParser(SeparatedTextObservationParser):

    def __init__(self):
        super(VegagerdinObservationParser, self).__init__(',', headers='(".*",)+".*"')
        self.meta['provider_ref'] = 'vg.is'

    def parse_header_line(self, line):
        """
        Parse header line, either extracting station reference or constructing field list for line parser.
        """
        if not super(VegagerdinObservationParser, self).parse_header_line(line):
            return False
        if line != '':
            parts = self.separator.split(line)
            parts = [p.strip('"') for p in parts]

            if len(parts) == 3:
                self.meta['station_ref'] = parts[1][-3:].lstrip('0')
                assert parts[1][-3:].lstrip('0') == str(int(parts[1][-3:]))
            else:
                self.field_list = parse_column_names(parts)
        return True

