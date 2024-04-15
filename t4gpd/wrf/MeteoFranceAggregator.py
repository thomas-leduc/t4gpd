'''
Created on 20 mar. 2024

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
'''
from t4gpd.commons.GeoProcess import GeoProcess


class MeteoFranceAggregator(GeoProcess):
    '''
    classdocs

    Données climatologiques de base - horaires
    https://meteo.data.gouv.fr/datasets/donnees-climatologiques-de-base-horaires
    '''

    def __init__(self, meteo, groupby=["NUM_POSTE", "month", "hour"]):
        '''
        Constructor
        '''
        self.meteo = meteo
        self.groupby = groupby

    @staticmethod
    def __agg(gdf, groupby):
        num_fields = list([f for f in gdf.select_dtypes(
            include="number") if (not f in ["NUM_POSTE", "ALTI", "LAT", "LON"])])
        aggfunc = {}
        for fieldname in gdf.columns:
            if ("geometry" != fieldname):
                if fieldname in num_fields:
                    aggfunc[fieldname] = "mean"
                else:
                    aggfunc[fieldname] = "first"
        gdf = gdf.dissolve(by=groupby, aggfunc=aggfunc)
        gdf.drop(columns=["timestamp", "AAAAMMJJHH"], inplace=True)
        return gdf

    def run(self):
        return MeteoFranceAggregator.__agg(self.meteo, self.groupby)


"""
from t4gpd.wrf.MeteoFranceReader import MeteoFranceReader

PERIODS = [
    # (1970, 1979),
    (1980, 1989),
    (1990, 1999),
    (2000, 2009),
    (2010, 2019),
    (2020, 2022),
    (2023, 2024),
]

rootdir = "/home/tleduc/data/meteofrance/data"
ifiles = [
    f"{rootdir}/HOR_departement_44_periode_{year0}-{year1}.csv"
    for year0, year1 in PERIODS
]
gdf = MeteoFranceReader(ifiles, station="NANTES-BOUGUENAIS").execute()

import matplotlib.pyplot as plt

for year0, year1 in PERIODS:
    gdf2 = gdf[ (year0 <= gdf.year) & (gdf.year <= year1) ]
    gdf3 = MeteoFranceAggregator(gdf2).execute()

    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(1.5 * 8.26, 1 * 8.26))
    fig.suptitle(f"Period {year0} - {year1}", fontsize=24)
    for month in range(12):
        nr, nc = month // 4, month % 4
        _gdf = gdf3[(gdf3.month == (1+month))]
        ax = axes[nr, nc]
        ax.set_title(f"Month {month+1}")
        ax.plot(_gdf.hour, _gdf.DNI, color="blue", label="DNI")
        ax.plot(_gdf.hour, _gdf.DHI, color="red", label="DHI")
        ax.plot(_gdf.hour, _gdf.GHI, color="green", label="GHI")
        ax.legend()
    fig.tight_layout()
    plt.savefig(f"DNI_DHI_GHI_{year0}_{year1}.pdf", bbox_inches="tight")
    # plt.show()
    plt.close(fig)
"""
