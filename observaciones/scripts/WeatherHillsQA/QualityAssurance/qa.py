# encoding: utf-8

"""

Provide interface for the quality assurance check of the data stored in a database.

Codes for the result of QA:
0 – pass
1 – suspect
2 – warning
3 – failed
8 – not tested
9 – missing

"""


from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import re
import os
import resource
from sqlalchemy.sql import select
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import izip
from sqlalchemy.sql.functions import max as sqlmax
from util.utilities import load_config, configure_logging, whLogger, utc, make_regexp
from util.db_connection import WHConnection
from util.calculator import parse_iso_date
from frtn import call_qa
# from frtn import make_frtn_input, save_frtn_input, call_frtn_code, read_frtn_output, process_frtn_output, get_call_id


LOG = whLogger(__name__)

GAP_TOLERANCE_DEFAULT = timedelta(hours=3)
mem_mb = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def get_station_info(conn, station_refs):

    """ Query the database for the metadata about stations with given refs. """

    if not station_refs:
        return []
    s_table = conn.get_table('station')
    s_columns = [getattr(s_table.c, col) for col in ['id', 'ref', 'lat', 'lon', 'has']]
    q = select(s_columns).where(s_table.c.ref.in_(station_refs))
    with conn.trans() as wht:
        result = wht.get_data(q)
    return [dict(r) for r in result]


def select_stations(conn, target):

    """ Select station refs for analysis based on a regexp-like station refs definition. """

    if not target:
        return []
    if type(target) in [str, basestring, unicode]:
        target = [target]
    s_table = conn.get_table('station')
    q = select([s_table.c.ref])
    with conn.trans() as wht:
        result = wht.get_data(q)
    all_refs = [r[0] for r in result]
    selected_refs = []

    for ref in target:
        ref = make_regexp(ref)
        selected_refs.extend([k for k in all_refs if re.match(ref, k)])

    return list(set(selected_refs))


def build_observation_query(conn, station_ids, variables, time_start, time_end, hourly=False):

    """ Build query to get appropriate observations from the database. """

    obs = conn.get_table('observation')

    data_columns = [getattr(obs.c, var) for var in variables]
    q = select([obs.c.time, obs.c.station_id] + data_columns)
    q = q.where(obs.c.station_id.in_(station_ids))
    q = q.where(time_start <= obs.c.time).where(obs.c.time <= time_end)

    if hourly:
        q = q.where(obs.c.time == func.date_trunc('hour', obs.c.time))
    return q


def get_previous_step_data(conn, station_ids, time_start, hourly=False):

    """
    Try to acquire the last timestamp before the selected dates,
    so that the step check can pass for the first entry in the day.
    """

    obs = conn.get_table('observation')

    q = select([sqlmax(obs.c.time)])
    q = q.where(obs.c.station_id.in_(station_ids)).where(obs.c.time < time_start)

    if hourly:
        q = q.where(obs.c.time == func.date_trunc('hour', obs.c.time))

    with conn.trans() as wht:
        result = wht.get_data(q)
    date = result[0][0]
    if date is None or time_start.replace(tzinfo=utc) - date > GAP_TOLERANCE_DEFAULT:
        return None
    return date


def get_data(conn, station_ids, variables, time_start, time_end, hourly=False):

    """
    Get the data from database and return it as a multi-dimensional dictionary of ts.date(), ts, variable and station_id,
    and values of (value, checked), where `checked` would indicate if this value was found in the QA results
    already present in DB, at the moment of getting data checked is False or None if value was None.
    The data for one timestamp prior to time_start is added to the dictionary, with checked = "prev_date".
    """

    LOG.info('Getting observational data')
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: (None, True)))))
    timestamps = set()

    previous = get_previous_step_data(conn, station_ids, time_start, hourly)
    query_time_start = previous if previous else time_start

    with conn.trans() as trans:
        query = build_observation_query(conn, station_ids, variables, query_time_start, time_end, hourly)
        result = trans.get_data(query)

    for line in iter(result):
        ts = line['time']
        timestamps.add(ts)
        date = ts.date()
        key = int(line['station_id'])

        for variable in variables:
            value = line[variable]
            checked = None if value is None else False
            if ts < time_start.replace(tzinfo=utc):
                checked = "prev_date"
            data[date][ts][variable][key] = (value, checked)

    return data, timestamps, previous


def result_dict_to_entries(qa_data, source_data, ghost_ts):

    """
    Convert the dictionary of QA results to entries ready to be inserted to the database.
    :param ghost_ts: timestamps that have been artificially added for proper behaviour of step_check
     (including previous timestamp that shouldn't be in this day's portion)
    """

    test_column_list = ['q_range', 'q_step', 'q_persistence', 'q_spatial']
    entries = []
    for var, val1 in qa_data.iteritems():
        for station, val2 in val1.iteritems():
            for ts, val3 in val2.iteritems():
                if ts in ghost_ts:
                    continue
                qa_list = qa_data[var][station][ts]
                (value, checked) = source_data[ts.date()][ts][var][station]
                if checked:
                    continue

                entry = {
                    'time': ts,
                    'variable': var,
                    'station_id': station,
                    'value': value
                }

                entry.update({test_column_list[i]: v for i, v in enumerate(qa_list)})
                entries.append(entry)
    return entries


def insert_qa_result(conn, result_entries, table='observation_quality'):

    """ Insert the QA result to the database """

    LOG.info('Inserting %d QA results to database', len(result_entries))
    conn.chunk_insert_manage_duplicates(result_entries, conn.get_table(table), chunk_size=50000)


def ts_by_day(timestamps, days_to_assess, tolerance=GAP_TOLERANCE_DEFAULT):

    """
    Yield daily portions of timestamps for Fortran processing, together with additional timestamps
    added for proper performance of QA. Additional timestamps can be added in between the data
    if difference between consecutive timestamps is less than tolerance.
    The last timestamp from a previous day, if within the tolerance, is also added to the list.
    """

    days_to_assess.sort()

    months_and_years = {(d.month, d.year) for d in days_to_assess}
    first_days_in_month = [min([d for d in days_to_assess if d.month == m and d.year == y]) for (m, y) in months_and_years]

    for day in days_to_assess:
        if day in first_days_in_month:
            LOG.info('Processing month %s/%s', day.month, day.year)
        step_check = []
        ts_for_day = sorted(list({ts for ts in timestamps if ts.date() == day}))
        try:
            previous_hour = max({ts for ts in timestamps if ts < ts_for_day[0]})
            if ts_for_day[0] - previous_hour <= tolerance:
                step_check.append(previous_hour)
        except ValueError:
            pass

        # Step check should fail if there are gaps in data,
        # but the Fortran program wouldn't know that as it doesn't get any timestamps
        # so we fake it with adding an empty entry in between.
        for ts1, ts2 in izip(ts_for_day[:-1], ts_for_day[1:]):
            if ts2 - ts1 > tolerance:
                step_check.append(ts1 + tolerance)
        ts_for_day.extend(step_check)
        yield sorted(ts_for_day), step_check


def slice_data(ts_for_day, data, station_ids, variables):

    """ Get a slice of the main data dictionary, according to the timestamps given. """

    subset = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

    used_ts = set()
    for day, for_day in data.iteritems():
        for ts, val1 in for_day.iteritems():
            if ts not in ts_for_day:
                continue
            used_ts.add(ts)
            for variable, val2 in val1.iteritems():
                for station_id, val3 in val2.iteritems():
                    subset[variable][station_id][ts] = data[ts.date()][ts][variable][station_id][0]

    for fake_ts in set(ts_for_day) - used_ts:
        for variable in variables:
            for station_id in station_ids:
                subset[variable][station_id][fake_ts] = None

    return subset


def find_already_inserted(conn, timestamps, station_data, variables, original_data, table='observation_quality', hourly=False):

    """ Get from the QA results table information about already checked observations. """

    LOG.info('Getting information about observations that have been evaluated before...')
    s_id_ref = {s['id']: s['ref'] for s in station_data}

    for key in s_id_ref.keys():
        oq = conn.get_table(table)
        q = select([oq.c.time, oq.c.variable])
        q = q.where(oq.c.station_id == key)
        q = q.where(oq.c.time.between(min(timestamps), max(timestamps)))
        q = q.where(oq.c.variable.in_(variables))

        if hourly:
            q = q.where(oq.c.time == func.date_trunc('hour', oq.c.time))

        with conn.trans() as wht:
            result = wht.get_data(q)

        for row in result:
            val = original_data[row['time'].date()][row['time']][row['variable']][key][0]
            original_data[row['time'].date()][row['time']][row['variable']][key] = (val, True)


def collect_days_to_assess(data):

    """
    If there is at least one value unchecked for that day (whichever timestamp, variable and station_id),
    the day should be assessed in the QA.
    """

    def check_day(day_data):
        for ts, d1 in day_data.iteritems():
            for var, d2 in d1.iteritems():
                for st, d3 in d2.iteritems():
                    if d3[1] is False:
                        return True
        return False

    to_assess = []
    for day, d in data.iteritems():
        if check_day(d):
            to_assess.append(day)

    return to_assess


def make_qa(conn, station_data, variables, time_start, time_end, gap_tolerance, remove_f_data=True, table='observation_quality', hourly=False):

    """ The main loop performing QA. """

    LOG.info('Time range for partial QA run: %s - %s', time_start, time_end)

    station_ids = [s['id'] for s in station_data]

    data, ts_set, previous = get_data(conn, station_ids, variables, time_start, time_end, hourly)

    if not data:
        LOG.warning('Empty observation set. Please make sure you have observations in database and that your start and end times are correct.')
        return

    LOG.debug('Memory usage after getting observations: %s MB', mem_mb())
    find_already_inserted(conn, ts_set, station_data, variables, data, table, hourly)
    to_assess = collect_days_to_assess(data)

    if not to_assess:
        LOG.info('No days to assess, it seems that all requested data is already in the database')
    else:
        LOG.info('Performing QA procedure in daily chunks')

    qa_results = []

    # call_id = get_call_id()

    LOG.debug('Memory usage after getting assessed data: %s MB', mem_mb())

    for ts_day_list, artificial_times in ts_by_day(ts_set, to_assess, tolerance=gap_tolerance):

        daily_slice = slice_data(ts_day_list, data, station_ids, variables)

        # Fortran daily processing
        # data_for_fortran = make_frtn_input(daily_slice, station_data, variables, ts_day_list)
        # save_frtn_input(data_for_fortran, call_id=call_id)
        # call_frtn_code(call_id=call_id, remove=remove_f_data)
        # raw_result = read_frtn_output(call_id=call_id, remove=remove_f_data)
        # dict_result = process_frtn_output(raw_result, station_ids, variables, ts_day_list)

        # QA processing rewritten
        dict_result = call_qa(daily_slice, station_data, variables, ts_day_list)

        result_for_db = result_dict_to_entries(dict_result, data, artificial_times)
        qa_results.extend(result_for_db)

        if len(qa_results) % 50000 < 5000:
            LOG.debug('Memory usage: %s MB', mem_mb())

        if len(qa_results) > 140000:
            insert_qa_result(conn, qa_results, table)
            qa_results = []

    if qa_results:
        insert_qa_result(conn, qa_results, table)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', required=True, help='Config file for program. Required')
    parser.add_argument('--log-config', default=os.path.join(os.path.dirname(__file__), 'logging.yml'),
                        help='Config file for logging. Defaults to logging.yml in code folder.')
    parser.add_argument('--start', help='Start date for QA', type=parse_iso_date, required=True)
    parser.add_argument('--end', help='End date for QA',
                        type=parse_iso_date, default=datetime.now().strftime('%Y-%m-%dT%H:%M'))
    parser.add_argument('--keep-f-data', help='Keep Fortran input and output data for debugging',
                        action='store_true', default=False)
    parser.add_argument('--qa-table', help='Target table for QA results, if different from `observation_quality`',
                        default='observation_quality')
    parser.add_argument('--hourly', help='Use when you want only the data from each full hour to be assessed',
                        action='store_true', default=False)
    return parser.parse_args()


def get_data_steps(n_stations, n_variables, time_start, time_end):

    """ Divide the time range into several consequent time periods to keep control on the memory during getting data. """

    rate_days = 20000
    chunk_size_days = round(rate_days / (n_stations * n_variables))

    chunk_size = timedelta(days=chunk_size_days)
    time = time_start
    times = []
    while time < time_end - chunk_size:
        times.append((time, time + chunk_size - timedelta(seconds=1)))
        time = time + chunk_size
    times.append((time, time_end))
    return times


def main():

    args = parse_args()
    config = load_config(args.config)
    configure_logging(args.log_config)

    db_conn = WHConnection(config['db_url'])

    variables = config['variables']
    if not variables:
        LOG.error("You didn't provide any variable name to make the QA for! ")
        LOG.error("You should add `variables: [your_v1, your_v2]` to your config file")
        raise ValueError("You didn't provide any variable name to make the QA for!")

    stations = config['stations']
    station_refs = select_stations(db_conn, stations)
    if not station_refs:
        LOG.error('Station refs list for %s is empty. Are you sure you request existing stations?' % str(stations))
        raise ValueError('Station refs list for %s is empty. Are you sure you request existing stations?' % str(stations))

    gap_tolerance = timedelta(minutes=config.get('gap_tolerance_minutes', 3 * 60))

    steps = get_data_steps(len(station_refs), len(variables), args.start, args.end)

    station_data = get_station_info(db_conn, station_refs)

    LOG.info('Station refs for QA run (%d): %s', len(station_data), ', '.join(sorted([s['ref'] for s in station_data])))
    LOG.info('Variables for QA run: %s', ', '.join(variables))

    LOG.info('Time range for QA run: %s - %s', args.start, args.end)

    for (start, end) in steps:
        make_qa(db_conn, station_data, variables, start, end, gap_tolerance,
                remove_f_data=not args.keep_f_data,
                table=args.qa_table,
                hourly=args.hourly)


if __name__ == '__main__':
    main()
