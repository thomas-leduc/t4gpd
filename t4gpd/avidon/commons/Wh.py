'''
Created on 27 mai 2021

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
from random import choice, randrange


class Wh(object):
    '''
    classdocs
    '''

    @staticmethod
    def computer():
        # 50 Wh < laptop < 100 Wh
        return 75.0

    @staticmethod
    def gateway():
        # 150 kWh/an < box < 300 kWh/an
        # return randrange(17, 35)
        return 26.0

    @staticmethod
    def tablet():
        # 2 Wh < tablet < 6 Wh
        return 4.0

    @staticmethod
    def smartobject():
        return 1.0

    @staticmethod
    def smartphone():
        # 10 Wh once a day!
        return 10.0

    @staticmethod
    def smartspeaker():
        # GHome: 5 Wh
        return 5.0

    @staticmethod
    def tv():
        # 40 Wh (Oled) < TV < 250 Wh (Plasma)
        # return choice([40.0] * 2 + [60.0] * 10 + [100.0] * 10 + [250.0] * 2)
        return 100.0
