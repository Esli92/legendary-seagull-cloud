# encoding: utf-8

"""

Parser for observations from Vedurstofa Islands

"""

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime
from parser import SeparatedTextObservationParser
from util.utilities import whLogger

mapping = {
    'F': 'wind_speed',
    'FG': 'wind_gust',
    'D': 'wind_dir',
    'T': 'temp',
    'P': 'pressure',
    'RH': 'rel_hum'
}


LOG = whLogger(__name__)


def float_or_no_data(s):
    s = s.strip()
    if s in ['#', '99999', '70000', '990']:
        return None
    return float(s)


def parse_time(s):
    return datetime.strptime(s, '%Y-%m-%d_%H:%M:%S.0')


class VedurstofanCsvObservationParser(SeparatedTextObservationParser):

    def __init__(self):
        super(VedurstofanCsvObservationParser, self).__init__(separator=',', headers='^#')
        self.meta['provider_ref'] = 'vi.is'

    def parse_header_line(self, line):
        if not super(VedurstofanCsvObservationParser, self).parse_header_line(line):
            return False
        if line != '':
            parts = self.separator.split(line[1:].strip())
            self.field_list = [('time', parse_time, parts.index('TIMI')), ('station_ref', str, parts.index('STOD'))]
            for key_in, key_out in mapping.iteritems():
                if key_in in parts:
                    self.field_list.append((key_out, float_or_no_data, parts.index(key_in)))
        return True