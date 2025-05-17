"""
Created on 22 mar. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from numpy import sqrt
from shapely import Point
from t4gpd.commons.proj.DoubleProjectionLib import DoubleProjectionLib


class DoubleProjectionLibTest(unittest.TestCase):

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
            result = DoubleProjectionLib.projection_switch(projectionName)
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
            result = DoubleProjectionLib.reverse_projection_switch(projectionName)
            self.assertEqual(
                expected, result.__name__, "Test reverse_projection_switch"
            )

    def test_isoaire_projection(self):
        k1 = 1 / (2 * sqrt(1 + 1 / sqrt(2)))
        k2 = 1 / (2 * sqrt(1 + sqrt(3) / 2))
        PAIRS = (
            ((0.5, 0.5, 1 / sqrt(2)), Point([k1, k1, 1])),
            ((0, 0.5, sqrt(3) / 2), Point([0, k2, 1])),
        )
        for rp, expected in PAIRS:
            result = DoubleProjectionLib.isoaire_projection(self.vp, rp, size=1)
            self.assertAlmostEqual(
                expected.distance(result),
                0,
                None,
                "Test isoaire projection",
                self.epsilon,
            )

    def test_orthogonal_projection(self):
        PAIRS = (
            ((0.5, 0.5, 1 / sqrt(2)), Point([0.5, 0.5, 1])),
            ((0, 0.5, sqrt(3) / 2), Point([0, 0.5, 1])),
        )
        for rp, expected in PAIRS:
            result = DoubleProjectionLib.orthogonal_projection(self.vp, rp, size=1)
            self.assertAlmostEqual(
                expected.distance(result),
                0,
                None,
                "Test orthogonal projection",
                self.epsilon,
            )

    def test_stereographic_projection(self):
        k1 = sqrt(2) / (sqrt(2) + 1)
        k2 = 2 / (2 + sqrt(3))
        PAIRS = (
            ((0.5, 0.5, 1 / sqrt(2)), Point([k1 / 2, k1 / 2, 1])),
            ((0, 0.5, sqrt(3) / 2), Point([0, k2 / 2, 1])),
        )
        for rp, expected in PAIRS:
            result = DoubleProjectionLib.stereographic_projection(self.vp, rp, size=1)
            self.assertAlmostEqual(
                expected.distance(result),
                0,
                None,
                "Test stereographic projection",
                self.epsilon,
            )

    def test_reverse_isoaire_projection(self):
        k1 = 1 / (2 * sqrt(1 + 1 / sqrt(2)))
        k2 = 1 / (2 * sqrt(1 + sqrt(3) / 2))
        PAIRS = (
            ((k1, k1, 0), Point([0.5, 0.5, 1 / sqrt(2)])),
            ((0, k2, 0), Point([0, 0.5, sqrt(3) / 2])),
        )
        for pp, expected in PAIRS:
            result = DoubleProjectionLib.reverse_isoaire_projection(self.vp, pp, size=1)
            self.assertAlmostEqual(
                expected.distance(result),
                0,
                None,
                "Test reverse isoaire projection",
                self.epsilon,
            )

    def test_reverse_orthogonal_projection(self):
        PAIRS = (
            ((0.5, 0.5, 0), Point([0.5, 0.5, 1 / sqrt(2)])),
            ((0, 0.5, 0), Point([0, 0.5, sqrt(3) / 2])),
        )
        for pp, expected in PAIRS:
            result = DoubleProjectionLib.reverse_orthogonal_projection(
                self.vp, pp, size=1
            )
            self.assertAlmostEqual(
                expected.distance(result),
                0,
                None,
                "Test reverse orthogonal projection",
                self.epsilon,
            )

    def test_reverse_stereographic_projection(self):
        k1 = sqrt(2) / (sqrt(2) + 1)
        k2 = 2 / (2 + sqrt(3))
        PAIRS = (
            ((k1 / 2, k1 / 2, 1), Point([0.5, 0.5, 1 / sqrt(2)])),
            ((0, k2 / 2, 1), Point([0, 0.5, sqrt(3) / 2])),
        )
        for pp, expected in PAIRS:
            result = DoubleProjectionLib.reverse_stereographic_projection(
                self.vp, pp, size=1
            )
            self.assertAlmostEqual(
                expected.distance(result),
                0,
                None,
                "Test reverse stereographic projection",
                self.epsilon,
            )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
