'''
Created on 6 juil. 2020

@author: tleduc

Copyright 2020 Thomas Leduc

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
import re


class CSVLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def readLexeme(s, decimalSep='.'):
        if ('.' != decimalSep):
            s = s.replace(decimalSep, '.')
        try:
            nb = float(s)
            if nb.is_integer():
                return int(nb)
            return nb
        except ValueError:
            pass
        try:
            import unicodedata
            nb = unicodedata.numeric(s)
            if nb.is_integer():
                return int(nb)
            return nb
        except (TypeError, ValueError):
            pass
        return s

    @staticmethod
    def read(inputFile, fieldSep=',', decimalSep='.'):
        rows, outputFields = [], []

        with open(inputFile, 'r') as f:
            for nline, line in enumerate(f, start=1):
                # values = line.strip().split(self.fieldSep)
                values = re.split(fieldSep, line.strip())
                values = [value.strip() for value in values]

                if (1 == nline):
                    for fieldName in values:
                        fieldName = fieldName.replace('"', '')
                        if (0 == len(fieldName)):
                            fieldName = 'gid'
                        outputFields.append(fieldName)
                else:
                    row = dict()
                    for i, value in enumerate(values):
                        value = value.replace('"', '')
                        row[outputFields[i]] = CSVLib.readLexeme(value, decimalSep)
                    rows.append(row)
        return rows
