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
from t4gpd.avidon.scenarios.AbstractScenario import AbstractScenario


class CredocBasedScenario(AbstractScenario):
    '''
    classdocs
    '''

    def _n_computers(self, row):
        # ~ (CREDOC, 2019, p. 42) - how to integrate data from Table 7, p. 43
        return (0.91 * row['Ind_11_17']
            +0.82 * row['Ind_18_24']
            +0.73 * row['Ind_25_39']
            +0.83 * row['Ind_40_54']
            +0.76 * row['Ind_55_64']
            +0.58 * row['Ind_65_79'])

    def _n_dsl(self, row):
        # ~ (CREDOC, 2019, p. 80)
        return (0.66 * self._n_gateways(row))

    def _n_gateways(self, row):
        # ~ (CREDOC, 2019, p. 76)
        return (0.86 * row['Men'])

    def _n_smartobjects(self, row):
        # ~ (CREDOC, 2019, p. 54)
        return (0.31 * row['Ind_11_17']
            +0.25 * row['Ind_18_24']
            +0.21 * row['Ind_25_39']
            +0.17 * row['Ind_40_54']
            +0.09 * row['Ind_55_64']
            +0.05 * row['Ind_65_79'])

    def _n_smartphones(self, row):
        # ~ (CREDOC, 2019, p. 35)
        return (0.86 * row['Ind_11_17']
            +0.98 * row['Ind_18_24']
            +0.95 * row['Ind_25_39']
            +0.80 * row['Ind_40_54']
            +0.62 * row['Ind_55_64']
            +0.44 * row['Ind_65_79'] 
            +0.0 * row['Ind_80p'])

    def _n_smartspeakers(self, row):
        # ~ (CREDOC, 2019, p. 49)
        return (0.15 * row['Ind_11_17']
            +0.14 * row['Ind_18_24']
            +0.10 * row['Ind_25_39']
            +0.09 * row['Ind_40_54']
            +0.07 * row['Ind_55_64']
            +0.05 * row['Ind_65_79'])

    def _n_tablets(self, row):
        # ~ (CREDOC, 2019, p. 46)
        return (0.37 * row['Ind_11_17']
            +0.36 * row['Ind_18_24']
            +0.49 * row['Ind_25_39']
            +0.45 * row['Ind_40_54']
            +0.47 * row['Ind_55_64']
            +0.29 * row['Ind_65_79'])

    def _n_tth(self, row):
        # ~ (CREDOC, 2019, p. 80)
        return (0.29 * self._n_gateways(row))

    def _n_tvs(self, row):
        # ~ Equipement des menages - 2018
        # ~ https://www.insee.fr/fr/statistiques/4277714
        return (0.792 * row['Ind_18_24']
            +0.931 * row['Ind_25_39']
            +0.953 * row['Ind_40_54']
            +0.979 * row['Ind_55_64']
            +0.979 * row['Ind_65_79'])
