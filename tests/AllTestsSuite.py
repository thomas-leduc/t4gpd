'''
Created on 1 avr. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
import unittest


class AllTestsSuite(unittest.TestCase):
    VERBOSITY = 3

    def __printResult(self, result):
        print('*****', result)
        _errors, _failures = result.errors, result.failures
        self.assertEqual(0, len(_errors), '*** errors = %d' % len(_errors))
        self.assertEqual(0, len(_failures), '*** failures = %d' % len(_failures))

    def testCommmons(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='./commons', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        result = runner.run(suite)
        self.__printResult(result)

    def testFuture(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='./future', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        result = runner.run(suite)
        self.__printResult(result)

    def testGraph(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='./graph', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        result = runner.run(suite)
        self.__printResult(result)

    def testIo(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='./io', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        result = runner.run(suite)
        self.__printResult(result)

    def testIsovist(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='./isovist', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        result = runner.run(suite)
        self.__printResult(result)

    def testMisc(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='./misc', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        result = runner.run(suite)
        self.__printResult(result)

    def testMorph(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='./morph', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        result = runner.run(suite)
        self.__printResult(result)

    def testSun(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='./sun', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        result = runner.run(suite)
        self.__printResult(result)

    '''
    def testRun(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir='.', pattern='*Test.py')
        # initialize a runner, pass it your suite and run it
        runner = unittest.TextTestRunner(verbosity=AllTestsSuite.VERBOSITY)
        self.__printResult(result)
    '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
