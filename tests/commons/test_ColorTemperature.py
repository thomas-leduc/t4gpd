'''
Created on 15 dec. 2020

@author: tleduc
'''
import unittest
from t4gpd.commons.ColorTemperature import ColorTemperature


class ColorTemperatureTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConvert_K_to_RGB(self):
        result = ColorTemperature.convert_K_to_RGB(2850)
        self.assertIsInstance(result, tuple, 'Is a tuple')
        self.assertEqual((255, 172, 99), result,
                         'Is equal to (255, 172, 99)')

        result = ColorTemperature.convert_K_to_RGB(5400)
        self.assertIsInstance(result, tuple, 'Is a tuple')
        self.assertEqual((255, 236, 219), result,
                         'Is equal to (255, 236, 219)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
