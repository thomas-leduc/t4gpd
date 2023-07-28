'''
Created on 15 dec. 2020

@author: tleduc
'''
import unittest
from shapely.geometry import Polygon
from t4gpd.commons.CaliperLib import CaliperLib


class CaliperLibTest(unittest.TestCase):

    def setUp(self):
        self.rectangle = Polygon([(1, 0), (3, 0), (4, 1), (3, 1.9), (1, 1.9), (0, 1), (1, 0)])
        pass

    def tearDown(self):
        pass

    def testMabr(self):
        rect, len1, len2 = CaliperLib.mabr(self.rectangle)
        self.assertIsInstance(rect, Polygon, 'MABR is a Polygon')
        self.assertTrue(len1 >= len2, 'MABR is a Polygon')
        print(rect, len1, len2)

    def testMpbr(self):
        rect, len1, len2 = CaliperLib.mpbr(self.rectangle)
        self.assertIsInstance(rect, Polygon, 'MPBR is a Polygon')
        self.assertTrue(len1 >= len2, 'MPBR is a Polygon')
        print(rect, len1, len2)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
