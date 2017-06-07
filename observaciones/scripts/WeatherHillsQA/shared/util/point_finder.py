
from __future__ import absolute_import, division, print_function, unicode_literals
import math
from util.db_connection import WHConnection
from util.utilities import whLogger

LOG = whLogger(__name__)

ASSUMED_SPATIAL_RESOLUTION_KM = 9


def get_required_radius(nn, res=ASSUMED_SPATIAL_RESOLUTION_KM):

    """ How far should we look to find nn points"""

    radius = ((math.ceil(nn ** 0.5 / math.pi)) + 1) * res
    return int(radius) * 1000  # [km]


def find_nearest_points(db_conn, target, schedule_ref, count):

    """ Find nearest points surrounding target in a grid for given schedule_ref"""

    radius = get_required_radius(count)

    LOG.info('Searching for %d nearest point(s)', count)

    query = """
        WITH stab AS (SELECT ll_to_earth(lat, lon) AS scoord FROM station WHERE ref=:station)
        SELECT point_id, lon, lat, i, j
        FROM grid_point join grid on (grid_point.id = grid.point_id)
        WHERE earth_box((SELECT scoord FROM stab), :radius) @> ll_to_earth(lat, lon)
        AND schedule_id = (SELECT id FROM schedule WHERE ref = :schedule)
        ORDER BY earth_distance(ll_to_earth(lat, lon), (SELECT scoord FROM stab)) limit :nn
    """

    with db_conn.trans() as wht:
        result = wht.get_data(query, station=target['ref'], radius=radius, schedule=schedule_ref, nn=count)

    if not result:
        raise ValueError('No points found around the station! Check the location of `%s` and the grid for schedule `%s`' % (target['ref'], schedule_ref))

    return [dict(r) for r in result]


def get_grid_point_info(db_conn, i, j, schedule_ref):

    """ Get point_id, lon, lat, i, j for the point with given i and j within certain schedule """

    query = """
        SELECT point_id, lon, lat, i, j
        FROM grid_point join grid on (grid_point.id = grid.point_id)
        WHERE i = :i AND j = :j AND schedule_id = (SELECT id FROM schedule WHERE ref = :schedule)
    """

    with db_conn.trans() as wht:
        result = wht.get_data(query, i=i, j=j, schedule=schedule_ref)
    return dict(result[0])


def find_grid_corner_points(db_conn, target, schedule_ref):

    """
    Find corner points surrounding target from a grid with given schedule_ref
    :type db_conn: WHConnection
    """

    LOG.info('Discovering grid corner points')

    nearest_point = find_nearest_points(db_conn, target, schedule_ref, 1)[0]

    x2_off = 1 if target['lon'] > nearest_point['lon'] else -1
    y2_off = 1 if target['lat'] > nearest_point['lat'] else -1

    return {
        (0, 0): nearest_point,
        (0, 1): get_grid_point_info(db_conn, nearest_point['i'], nearest_point['j'] + y2_off, schedule_ref),
        (1, 0): get_grid_point_info(db_conn, nearest_point['i'] + x2_off, nearest_point['j'], schedule_ref),
        (1, 1): get_grid_point_info(db_conn, nearest_point['i'] + x2_off, nearest_point['j'] + y2_off, schedule_ref)
    }
