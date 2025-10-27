"""
Created on 11 juin 2020

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

from timeit import default_timer as timer


class GeoProcess(object):
    """
    classdocs
    """

    def __elapsedTime(self, start, stop):
        """
        Print elapsed time between start and stop.
        :param start: start time
        :param stop: stop time
        """
        delta = stop - start
        h, m, s = (
            int(delta) // 3600,
            (int(delta) % 3600) // 60,
            (int(delta) % 3600) % 60,
        )
        print(f"Elapsed time: {delta:.3f} s ({h:02d}:{m:02d}:{s:02d})")

    def execute(self):
        """
        Execute the process and measure the elapsed time.
        :return: result of the process
        """
        start = timer()
        result = self.run()
        stop = timer()
        self.__elapsedTime(start, stop)
        return result

    def executeWithArgs(self, args):
        """
        Execute the process with arguments and measure the elapsed time.
        :param args: arguments for the process
        :return: result of the process
        """
        start = timer()
        result = self.runWithArgs(args)
        stop = timer()
        self.__elapsedTime(start, stop)
        return result

    def run(self):
        raise NotImplementedError("subclasses must override run()!")

    def runWithArgs(self, args):
        raise NotImplementedError("subclasses must override runWithArgs()!")

    def updateOrAppend(self, inSeries, addDict):
        """
        Update the input series with the values from addDict. If a key in addDict does not exist in inSeries, it will be added.
        :param inSeries: input series (dict-like)
        :param addDict: dictionary with values to add or update
        :return: updated series
        """
        result = dict(inSeries)
        result.update(addDict)
        return result

    def appendNewItems(self, inSeries, addDict):
        """
        Append new items from addDict to inSeries. If a key in addDict does not exist in inSeries, it will be added.
        :param inSeries: input series (dict-like)
        :param addDict: dictionary with values to add
        :return: updated series with new items
        """
        result = dict(inSeries)
        for k, v in addDict.items():
            if k not in result:
                result[k] = v
        return result
