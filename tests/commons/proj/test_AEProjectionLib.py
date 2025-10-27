"""
Created on 22 mar. 2024

@author: tleduc

Copyright 2020-2025 Thomas Leduc

This file is part of t4gpd.

t4gpd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

t4gpd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with t4gpd.  If not, see <https://www.gnu.org/licenses/>.
"""

import unittest
from numpy import cos, pi, sin, sqrt
from shapely import Point
from t4gpd.commons.proj.AEProjectionLib import AEProjectionLib


class AEProjectionLibTest(unittest.TestCase):
    def setUp(self):
        self.vp = (0, 0, 0)
        self.epsilon = 1e-9

    def tearDown(self):
        pass

    def test_projection_switch(self):
        PAIRS = [
            ("Isoaire", "isoaire_projection"),
            ("Equiareal", "isoaire_projection"),
            ("Orthogonal", "orthogonal_projection"),
            ("Stereographic", "stereographic_projection"),
            ("Polar", "polar_projection"),
        ]
        for projectionName, expected in PAIRS:
            result = AEProjectionLib.projection_switch(projectionName)
            self.assertEqual(expected, result.__name__, "Test projection_switch")

    def test_reverse_projection_switch(self):
        PAIRS = [
            ("Isoaire", "reverse_isoaire_projection"),
            ("Equiareal", "reverse_isoaire_projection"),
            ("Orthogonal", "reverse_orthogonal_projection"),
            ("Stereographic", "reverse_stereographic_projection"),
            ("Polar", "reverse_polar_projection"),
        ]
        for projectionName, expected in PAIRS:
            result = AEProjectionLib.reverse_projection_switch(projectionName)
            self.assertEqual(
                expected, result.__name__, "Test reverse_projection_switch"
            )

    def test_isoaire_projection(self):
        trios = (
            (0, pi / 4, Point(sqrt(2) * sin(pi / 8), 0)),
            (pi / 4, pi / 4, Point(sin(pi / 8), sin(pi / 8))),
            (pi / 2, pi / 4, Point(0, sqrt(2) * sin(pi / 8))),
        )
        for azim, elev, expected in trios:
            actual = AEProjectionLib.isoaire_projection(self.vp, azim, elev, size=1)
            self.assertAlmostEqual(
                expected.distance(Point(actual)),
                0,
                None,
                "Test isoaire projection",
                self.epsilon,
            )

    def test_orthogonal_projection(self):
        trios = (
            (0, pi / 4, Point(1 / sqrt(2), 0)),
            (pi / 4, pi / 4, Point(1 / 2, 1 / 2)),
            (pi / 2, pi / 4, Point(0, 1 / sqrt(2))),
        )
        for azim, elev, expected in trios:
            actual = AEProjectionLib.orthogonal_projection(self.vp, azim, elev, size=1)
            self.assertAlmostEqual(
                expected.distance(Point(actual)),
                0,
                None,
                "Test orthogonal projection",
                self.epsilon,
            )

    def test_stereographic_projection(self):
        k1 = sqrt(2) / (sqrt(2) + 1)
        k2 = 1 / (sqrt(2) + 1)
        trios = (
            (0, pi / 2, Point(0, 0)),
            (pi / 4, pi / 4, Point(k1 / 2, k1 / 2)),
            (0, pi / 4, Point(k2, 0)),
        )
        for azim, elev, expected in trios:
            actual = AEProjectionLib.stereographic_projection(
                self.vp, azim, elev, size=1
            )
            self.assertAlmostEqual(
                expected.distance(Point(actual)),
                0,
                None,
                "Test stereographic projection",
                self.epsilon,
            )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
