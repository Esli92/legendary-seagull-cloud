"""

Sanity check for the data to be inserted into DB

"""

from __future__ import absolute_import, division, print_function, unicode_literals
from util.utilities import whLogger
LOG = whLogger(__name__)

constraints = {
    'wind_dir': (0, 360),
    'wind_speed': (0, float('inf')),
    'wind_gust': (0, float('inf')),
    'rel_hum': (0, 200.0),
    'temp': (-273.15, 100.0),
    'pressure': (100.0, 1700.0),
    'mslp': (100.0, 1100.0),
    'temp_road': (-273.15, 100.0),
    'snow_ratio': (0, 1.0),
    'prec_rate': (0, float('inf'))
}

# probably we can also add `weak constraints` to illustrate most near-to-ground cases, such as temperature
# between world record minimum and maximum


def check_data_sanity(entries, fail_outside_range=True, log_warning=True):

    """
    Scans through all entries to be inserted into DB to check if any of variables has a totally improper value.
    If fail_outside_range is True, raises an error when found any such a problem, to indicate that probably
    wrong numbers were parsed to be values of given variables. Otherwise it in-place changes appropriate value to None.
    """

    LOG.info('Performing sanity check...')
    for entry in entries:
        for k, v in entry.iteritems():
            if k not in constraints:
                continue

            mini, maxi = constraints[k]
            if mini <= v <= maxi or v is None:
                continue

            fail_msg = 'Incorrect value for component %s: %s' % (k, str(v))  # (explicit instead of default==bad formatting)
            if fail_outside_range:
                LOG.error(fail_msg)
                raise ValueError(fail_msg)
            else:
                if log_warning:
                    LOG.warning(fail_msg + '. Replacing with None')
                entry[k] = None
