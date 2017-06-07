# encoding: utf-8

"""

All functions that have to do with Fortran QA executable: preparing and saving the data, running and parsing the output.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import codecs
import uuid
from subprocess import check_call, CalledProcessError
from collections import defaultdict
from util.utilities import whLogger
import numpy
from core import range_check, step_check, persistence_check, spatial_check

LOG = whLogger(__name__)

CALL_ID_DEFAULT = 'p'

FRTN_PATH = os.path.join(os.path.dirname(__file__), 'frtn')

NODATA = -888888.0

FRTN_VAR_MAP = {
    'temp': 'temp',
    'wind_speed': 'wsp',
    'wind_dir': 'wdir',
    'rel_hum': 'rh'
}


def data_to_text(data, variables, stations, timestamps):

    """
    Given dictionary-like data and a list of keys (vars, stations, ts),
    convert them to text understood by the Fortran program.
    """

    txt = ''
    for variable in variables:
        for station in stations:
            for ts in timestamps:

                val = data[variable][station][ts]
                val = NODATA if val is None else val + (273.15 if variable == 'temp' else 0)

                txt += '%20.4f' % val
    return txt


def call_frtn_code(call_id=CALL_ID_DEFAULT, remove=True):

    """ Use subprocess to call the external Fortran program. """

    LOG.debug('Calling external Fortran executable for quality control.')
    try:
        check_call('cd {} ; ./run_qa {} > /dev/null'.format(FRTN_PATH, call_id), shell=True)
        if remove:
            os.remove(os.path.join(FRTN_PATH, '{}_input.txt'.format(call_id)))
    except CalledProcessError as e:
        LOG.exception(e)
        raise


def check_none(value):

    """ Replace Nones with NODATA value. """

    if value is None:
        return NODATA
    return value


def input_to_arrays(data, station_info, variables, timestamps):
    obs = numpy.ndarray((len(timestamps), len(station_info), len(variables)))
    lon = numpy.ndarray((len(timestamps), len(station_info)))
    lat = numpy.ndarray((len(timestamps), len(station_info)))
    has = numpy.ndarray((len(timestamps), len(station_info)))

    for i, ts in enumerate(timestamps):
        for j, st in enumerate(station_info):
            lon[i, j] = check_none(st['lon'])
            lat[i, j] = check_none(st['lat'])
            has[i, j] = check_none(st['has'])
            for k, var in enumerate(variables):
                val = data[var][st['id']][ts]
                obs[i, j, k] = NODATA if val is None else val + (273.15 if var == 'temp' else 0)

    return obs, lon, lat, has


def arrays_to_output(qa_result, station_ids, variables, timestamps):
    LOG.debug('Building result from QA output')
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for i, ts in enumerate(timestamps):
        for j, st in enumerate(station_ids):
            for k, var in enumerate(variables):
                data[var][st][ts] = list(qa_result[i][j][k])
    return data


def call_qa(data, station_info, variables, timestamps):
    qc_flag = numpy.ndarray((len(timestamps), len(station_info), len(variables), 4))
    obs, lon, lat, has = input_to_arrays(data, station_info, variables, timestamps)

    for ivar, var in enumerate(variables):
        range_check(obs, len(station_info), var, ivar, qc_flag)
        step_check(obs, len(station_info), var, ivar, qc_flag)
        persistence_check(obs, len(station_info), var, ivar, qc_flag)
        spatial_check(obs, len(station_info), lat, lon, has, var, ivar, qc_flag)

    data = arrays_to_output(qc_flag, [s['id'] for s in station_info], variables, timestamps)
    return data


def make_frtn_input(data, station_info, variables, timestamps):

    """ Prepare the lines for Fortran program input. """

    LOG.debug('Preparing input data for QA for %s.', sorted(timestamps)[-1].date())
    lines = [
        '{} {} {}'.format(len(timestamps), len(station_info), len(variables)),
        ' '.join(['{:<10}'.format(s['ref']) for s in station_info]),
        ' '.join(['{:<10}'.format(FRTN_VAR_MAP[v]) for v in variables]),
        ' '.join(map(str, [check_none(s['lat']) for s in station_info for _ in timestamps])),
        ' '.join(map(str, [check_none(s['lon']) for s in station_info for _ in timestamps])),
        ' '.join(map(str, [check_none(s['has']) for s in station_info for _ in timestamps])),
        data_to_text(data, variables, [s['id'] for s in station_info], timestamps)
    ]
    return lines


def get_call_id():
    return str(uuid.uuid4())


def save_frtn_input(lines, call_id=CALL_ID_DEFAULT):

    """ Save the input for Fortran program. """

    filename = os.path.join(FRTN_PATH, '{}_input.txt'.format(call_id))
    LOG.debug('Saving temporary file for Fortran in %s', filename)
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as fi:
            fi.write('\n'.join(lines))
    except Exception as e:
        LOG.exception(e)
        raise


def read_frtn_output(call_id=CALL_ID_DEFAULT, remove=True):

    """ Read the output of Fortran program and return it as a list of integer values. """

    filename = os.path.join(FRTN_PATH, '{}_result.txt'.format(call_id))
    LOG.debug('Reading the output of Fortran program from %s', filename)
    with open(filename) as in_data:
        raw_result = map(int, in_data.read().split())
    if remove:
        os.remove(filename)
    return raw_result


def process_frtn_output(raw_result, stations, variables, timestamps, test_count=4):

    """ Process the raw Fortran output according to known data about stations, variables and timestamps. """

    LOG.debug('Building result from Fortran output')

    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for test in range(test_count):
        for var in variables:
            for station in stations:
                for ts in timestamps:
                    data[var][station][ts].append(raw_result.pop(0))
    return data
