'''
Created on 29 avr. 2023

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
'''
from io import StringIO, TextIOWrapper
import unittest

from t4gpd.io.AbstractReader import AbstractReader


class AbstractReaderTest(unittest.TestCase):

    def setUp(self):
        self.sio = StringIO("ceci est un test")
        self.filename = __file__

    def tearDown(self):
        pass

    def testOpener(self):
        for _ in range(3):
            # Re-open several times
            with AbstractReader.opener(self.sio) as f:
                self.assertIsInstance(f, StringIO, "Is a StringIO")

            with AbstractReader.opener(self.filename) as f:
                self.assertIsInstance(f, TextIOWrapper, "Is a TextIOWrapper")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
