from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime
from parser import SeparatedTextObservationParser


FIELD_ALIASES = {
    'QNH (mb)': 'pressure',
    '10 Min AirTemp': 'temp',
    '10 Min RH': 'rel_hum',
    '2 Min WD 03': 'wind_dir',
    '2 Min WS 03': 'wind_speed'
}


def float_or_no_data(s):
    s = s.strip()
    if not s or s in ['9999']:
        return None
    return float(s)


def parse_time(s):
    return datetime.strptime(s, '%d/%m/%Y %H:%M')


class CaboVerdeObservationParser(SeparatedTextObservationParser):

    def __init__(self):
        super(CaboVerdeObservationParser, self).__init__(separator=',', headers='[^,]*[a-zA-Z]+[^,]*(,.*[a-zA-Z]+.*)*$')
        self.meta['provider_ref'] = 'inmg.cv'

    def parse_header_line(self, line):
        if not super(CaboVerdeObservationParser, self).parse_header_line(line):
            return False
        if line != '':
            parts = self.separator.split(line.strip())
            self.field_list = [('time', parse_time, parts.index('DD/MM/YYYY HH:MM')), ('station_ref', str, parts.index('Site Identifier'))]
            for key_in, key_out in FIELD_ALIASES.iteritems():
                if key_in in parts:
                    self.field_list.append((key_out, float_or_no_data, parts.index(key_in)))
        return True

    def parse_data_line(self, line):
        obs = super(CaboVerdeObservationParser, self).parse_data_line(line)
        if obs['time'].minute != 0:
            return None
        return obs

