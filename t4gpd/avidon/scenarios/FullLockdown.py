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
from t4gpd.avidon.commons.Wh import Wh
from t4gpd.avidon.scenarios.CredocBasedScenario import CredocBasedScenario


class FullLockdown(CredocBasedScenario):
    '''
    classdocs
    '''
    def energyDemandOfITEquipment(self, row, dt):
        hour, weekday = dt.hour, dt.weekday()

        wh = (
            self._n_gateways(row) * Wh.gateway()
            +self._n_smartobjects(row) * Wh.smartobject()
            +self._n_smartspeakers(row) * Wh.smartspeaker()
            )

        if (self.is_weekend(dt)):
            wh += (
                self._n_computers(row) * Wh.computer() * (14 <= hour <= 20)
                +self._n_smartphones(row) * Wh.smartphone() * (hour in [9, 20])
                +self._n_tablets(row) * Wh.tablet() * ((9 <= hour <= 12) or (14 <= hour <= 20))
                +self._n_tvs(row) * Wh.tv() * (9 <= hour <= 23)
                )
        else:
            wh += (
                self._n_computers(row) * Wh.computer() * ((9 <= hour <= 12) or (14 <= hour <= 20))
                +self._n_smartphones(row) * Wh.smartphone() * (21 == hour)
                +self._n_tablets(row) * Wh.tablet() * ((7 <= hour <= 9) or (19 <= hour <= 21))
                +self._n_tvs(row) * Wh.tv() * ((7 <= hour <= 9) or (13 == hour) or (19 <= hour <= 22))
                )

        return wh
