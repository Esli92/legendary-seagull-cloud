# encoding: utf-8

"""

Parsers for Belgingur's standard data format(s)

"""

from __future__ import absolute_import, division, print_function, unicode_literals
import re

from parser import SeparatedTextObservationParser, InsufficientHeaders
from util.calculator import parse_iso_date
from util.utilities import whLogger


LOG = whLogger(__name__)

HEADER_SEPARATOR = re.compile('\s*[:=\s]\s*')
""" Separates name from value in headers. """

FIELD_ALIASES = {
    'timestamp': 'time',
    'precipitation': 'prec_rate',
    'prec': 'prec_rate',
}
""" Alternate names for field, so we can accept files using slightly different names. """

FLOAT_FIELDS = ('wind_speed', 'wind_dir', 'wind_gust',
                'temp', 'temp_road', 'temp_ground',
                'pressure', 'rel_hum', 'air_density')


class BelgingurObservationParser(SeparatedTextObservationParser):
    """
    Belgingur-standard observation files. They consist of:

    * any number of header lines of the form `## key: value` where key and value are separated by white-space and optionally a : or =
    * exactly one
    """

    def __init__(self):
        super(BelgingurObservationParser, self).__init__('\s*[,\s]\s*')

    def pick_converter(self, name):
        if name in FLOAT_FIELDS:
            return float
        if name in ('time',):
            return parse_iso_date
        return str

    def add_field(self, i, name):
        name = name.replace('.', '_').replace('-', '_')
        name = FIELD_ALIASES.get(name, name)
        converter = self.pick_converter(name)
        self.field_list.append((name, converter, i))

    def parse_header_line(self, line):
        """
        :type line: string
        """
        if line == '':
            return True
        if line.startswith('##'):
            line = line[2:].strip()
            parts = HEADER_SEPARATOR.split(line, 1)
            if len(parts) == 2:
                self.meta[parts[0]] = parts[1]
            return True
        if line.startswith('#'):
            if len(self.field_list) > 0:
                raise ValueError('We only expect one header line starting with a single "#" for column labels.')
            parts = self.separator.split(line[1:].strip())
            for i, part in enumerate(parts):
                self.add_field(i, part)
            return True

        if len(self.field_list) == 0:
            raise InsufficientHeaders('We expect exactly one one header line starting with a single "#" for column labels.')
        return False
