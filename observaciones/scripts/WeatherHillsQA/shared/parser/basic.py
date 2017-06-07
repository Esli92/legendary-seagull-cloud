# encoding: utf-8

"""

Basic parser for a comma-separated data format with header line(s).

Metadata defined as lines starting with '#' and in 'key: value' format.
A minimum set of metadata keys is {'provider_ref', 'station_ref'}.
'station_ref' is how you call the station in your system, corresponding to the column `ref_provider` in `station` table.
Then one header line with column names.
Your time must be in ISO format, e.g. 2016-01-01T12:00:00.
Your nodata should be marked as --- or -9999.0 or -9999.
Your column names must agree with the database table column names reflected in AVAILABLE_FIELDS.

When having your provider name known, you can define your own parser as a subclass of CSVWithHeadersObservationParser
and adding self.meta['provider_ref'] = 'your.provider.name' in the __init__.

"""


from __future__ import absolute_import, division, print_function, unicode_literals

from parser import SeparatedTextObservationParser, InsufficientHeaders
from util.calculator import parse_iso_date
from util.utilities import whLogger

LOG = whLogger(__name__)

HEADER_SEPARATOR = ':'


AVAILABLE_FIELDS = [
    'wind_dir', 'wind_speed', 'wind_gust', 'temp', 'temp_road', 'pressure', 'rel_hum',
    'dew', 'precip', 'vis', 'clouds', 'swdown', 'lwdown', 'weather'
]
"""Reflect the variables columns in observation table"""


def float_or_no_data(s):
    if s in ['---', '-9999.0', '-9999']:
        return None
    return float(s)


class CSVWithHeadersObservationParser(SeparatedTextObservationParser):

    def __init__(self):
        super(CSVWithHeadersObservationParser, self).__init__(separator=',', headers='^#|[^,]*[a-zA-Z]+[^,]*(,[^,]*[a-zA-Z]+[^,]*)*$')

    def parse_header_line(self, line):
        if not super(CSVWithHeadersObservationParser, self).parse_header_line(line):
            return False
        if line == '':
            return True

        if line.startswith('#'):
            k, v = line[1:].strip().split(HEADER_SEPARATOR, 1)
            self.meta[k.strip()] = v.strip()
        else:
            parts = self.separator.split(line.strip())
            parts = [p.strip() for p in parts]

            if 'provider_ref' not in self.meta:
                raise InsufficientHeaders("Provider reference not found. "
                                          "Define it at the top of your csv as `# provider_ref: your.ref.name` ")
            if 'station_ref' not in self.meta:
                raise InsufficientHeaders("Station reference not found. "
                                          "Define it at the top of your csv as `# station_ref: your.ref.name` ")

            self.field_list = [('time', parse_iso_date, parts.index('time'))]
            for key_in in AVAILABLE_FIELDS:
                if key_in in parts:
                    self.field_list.append((key_in, float_or_no_data, parts.index(key_in)))
            remaining_columns = set(parts) - set([f[0] for f in self.field_list])
            if remaining_columns:
                LOG.warning('The following columns in your data were not recognized by the parser: %s', ', '.join(remaining_columns))
        return True

    def parse_data_line(self, line):
        return super(CSVWithHeadersObservationParser, self).parse_data_line(line.strip())
