from parser import SeparatedTextObservationParser, InsufficientHeaders
from datetime import datetime


def float_or_na(s):
    if s == '':
        return None
    return round(float(s), 4)


def parse_date(d, t):
    return datetime.strptime('{}_{}'.format(d, t), '%m/%d/%Y_%H:%M')


def parse_temperature(s):
    t = float_or_na(s)
    return t if t is None else t - 273.15


def parse_pressure(s):
    p = float_or_na(s)
    return p if p is None else round(p / 100.0, 4)


def pick_provider_ref(s):
    provider_refs = {
        'OTHER-MTR': 'af.mtr',
        'APRSWXNET': 'af.cwop',
        'MARITIME': 'af.mar'
    }
    return provider_refs[s]


field_list = [
    ('time', parse_date, 1, 2),
    ('dew', parse_temperature, 5),
    ('rel_hum', float_or_na, 6),
    ('pressure', parse_pressure, 7),
    ('temp', parse_temperature, 8),
    ('wind_dir', float_or_na, 9),
    ('wind_speed', float_or_na, 10),
    ('station_ref', lambda s: s.strip(), 0),
    ('provider_ref', pick_provider_ref, 3)
]


class MADISObservationParser(SeparatedTextObservationParser):
    def __init__(self):
        super(MADISObservationParser, self).__init__(' *, *', field_list)

#td rh p t dd ff
