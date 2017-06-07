from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
from util.db_tables import create_tables
from util.point_finder import *
from util.tests import make_WHConnection


class TestPointFinder(TestCase):
    def setUp(self):
        self.db_conn = make_WHConnection()
        create_tables(self.db_conn.engine)

        self.points = [
            {'lat': 49.220014, 'lon': 20.011048, 'i': None, 'j': None}, #swinica
            {'lat': 49.219201, 'lon': 20.016541, 'i': None, 'j': None}, #zawrat
            {'lat': 49.225046, 'lon': 19.992273, 'i': None, 'j': None}, #liliowe
            {'lat': 49.232760, 'lon': 19.982821, 'i': None, 'j': None}, #PKL Kasprowy
            {'lat': 49.242626, 'lon': 20.007191, 'i': None, 'j': None}, #Murowaniec
            {'lon': 0, 'lat': 0, 'i': 100, 'j': 51},
            {'lon': 0.02, 'lat': 0, 'i': 101, 'j': 51},
            {'lon': 0, 'lat': 0.02, 'i': 100, 'j': 52},
            {'lon': 0.02, 'lat': 0.02, 'i': 101, 'j': 52}
        ]
        self.stations = [
            {'lat': 49.2324, 'lon': 19.9819, 'ref': 'kas', 'name': 'Kasprowy Wierch Observatory'},
            {'lon': 0.005, 'lat': 0.005, 'ref': 'is.left.down', 'name': 'Left Down'},
            {'lon': 0.015, 'lat': 0.005, 'ref': 'is.right.down', 'name': 'Right Down'},
            {'lon': 0.005, 'lat': 0.015, 'ref': 'is.left.up', 'name': 'Left Up'},
            {'lon': 0.015, 'lat': 0.015, 'ref': 'is.right.up', 'name': 'Right Up'}
        ]

        with self.db_conn.trans() as wht:
            self.schedule_id = wht.insert_single_entry({'ref': 'test'}, self.db_conn.get_table('schedule'))
            self.provider_id = wht.insert_single_entry({'ref': 'PF', 'name': 'PointFinder'}, self.db_conn.get_table('provider'))
            for station in self.stations:
                station.update({'provider_id': self.provider_id})
                wht.insert_single_entry(station, self.db_conn.get_table('station'))

            for i, point in enumerate(self.points):
                point_id = wht.insert_single_entry({'lon': point['lon'], 'lat': point['lat']}, self.db_conn.get_table('grid_point'))
                wht.insert_single_entry({'point_id': point_id, 'schedule_id': self.schedule_id, 'i': point['i'], 'j': point['j']}, self.db_conn.get_table('grid'))
                self.points[i].update({'point_id': point_id})

    def test_find_nearest_points(self):
        nearest_points = find_nearest_points(self.db_conn, self.stations[0], 'test', 1)
        self.assertListEqual([self.points[3]], nearest_points)

        nearest_points = find_nearest_points(self.db_conn, self.stations[0], 'test', 2)
        self.assertListEqual([self.points[3], self.points[2]], nearest_points)

        nearest_points = find_nearest_points(self.db_conn, self.stations[0], 'test', 3)
        self.assertListEqual([self.points[3], self.points[2], self.points[4]], nearest_points)

        nearest_points = find_nearest_points(self.db_conn, self.stations[0], 'test', 4)
        self.assertListEqual([self.points[3], self.points[2], self.points[4], self.points[0]], nearest_points)

        nearest_points = find_nearest_points(self.db_conn, self.stations[0], 'test', 5)
        self.assertListEqual([self.points[3], self.points[2], self.points[4], self.points[0], self.points[1]], nearest_points)

    def test_find_grid_corner_points(self):
        corner_points = find_grid_corner_points(self.db_conn, self.stations[1], 'test')
        expected = {(0, 0): self.points[5], (1, 1): self.points[8], (1, 0): self.points[6], (0, 1): self.points[7]}
        self.assertDictEqual(expected, corner_points)

        corner_points = find_grid_corner_points(self.db_conn, self.stations[2], 'test')
        expected = {(0, 0): self.points[6], (1, 1): self.points[7], (1, 0): self.points[5], (0, 1): self.points[8]}
        self.assertDictEqual(expected, corner_points)

        corner_points = find_grid_corner_points(self.db_conn, self.stations[3], 'test')
        expected = {(0, 0): self.points[7], (1, 1): self.points[6], (1, 0): self.points[8], (0, 1): self.points[5]}
        self.assertDictEqual(expected, corner_points)

        corner_points = find_grid_corner_points(self.db_conn, self.stations[4], 'test')
        expected = {(0, 0): self.points[8], (1, 1): self.points[5], (1, 0): self.points[7], (0, 1): self.points[6]}
        self.assertDictEqual(expected, corner_points)

    def tearDown(self):
        with self.db_conn.trans() as wht:
            wht.execute("delete from station where provider_id=:prid; delete from provider where id=:prid", prid=self.provider_id)
            wht.execute("delete from grid where schedule_id=:sid; delete from schedule where id=:sid", sid=self.schedule_id)
            for point in self.points:
                wht.execute("delete from grid_point where id = :pid", pid=point['point_id'])



