'''
Created on 12 jan. 2024

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
from datetime import timedelta, timezone
from geopandas import GeoDataFrame
from multiprocessing import Pool
from numpy import cos, pi
from pandas import concat, read_csv, to_datetime
from pvlib.irradiance import dirint
from shapely import Point
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.sun.SunLib import SunLib


class MeteoFranceReader(GeoProcess):
    '''
    classdocs

    Données climatologiques de base - horaires
    https://meteo.data.gouv.fr/datasets/donnees-climatologiques-de-base-horaires
    '''

    def __init__(self, ifiles, station="NANTES-BOUGUENAIS", tzinfo=timezone.utc,
                 ocrs="epsg:2154", model="pysolar", encode=False):
        '''
        Constructor
        '''
        self.ifiles = ifiles
        self.station = station
        # DEBUG DU 17.01.2024 :
        # Les releves des stations MeteoFrance sont en temps UTC
        self.tzinfo = tzinfo
        self.ocrs = ocrs
        self.model = model
        self.encode = encode

    @staticmethod
    def __read(ifile, station, tzinfo):
        df = read_csv(ifile, decimal=".", encoding="utf8", sep=";")
        if station is not None:
            df = df[df.NOM_USUEL == station]
        df["timestamp"] = df.AAAAMMJJHH.apply(
            lambda v: to_datetime(str(v), format="%Y%m%d%H", utc=False).
            replace(tzinfo=tzinfo))
        cols = {}
        for fieldname in [" FXI", " DHUMEC", " N", " SOL", " T", " TUBENEIGE", " UV"]:
            if fieldname in df:
                cols[fieldname] = fieldname.replace(" ", "")
        df.rename(columns=cols, inplace=True)
        df.reset_index(drop=True, inplace=True)
        # REMOVE EMPTY COLUMNS
        # df.dropna(axis=1, inplace=True, how="all")
        return df

    @staticmethod
    def __enrich(df, ocrs, model, encode):
        # DEBUG DU 17.01.2024 :
        # LE CHAMP GLO2 EST SYSTEMATIQUEMENT RENSEIGNE... CONTRAIREMENT
        # AU CHAMP GLO (QUI NE L'EST QUE DEPUIS LES ANNEES 2000)
        # GLO2 = rayonnement global horaire en heure TSV (en J/cm2)
        # TSV = Temps Solaire Vrai (Apparent solar time or true solar time)
        longitude = df.at[0, "LON"]
        df.timestamp = df.timestamp.apply(
            lambda dt: dt + timedelta(hours=(longitude*12/180)))

        df["year"] = df.timestamp.apply(lambda dt: dt.year)
        df["month"] = df.timestamp.apply(lambda dt: dt.month)
        df["day"] = df.timestamp.apply(lambda dt: dt.day)
        df["hour"] = df.timestamp.apply(lambda dt: dt.hour)
        df["day_of_year"] = df.timestamp.apply(lambda dt: dt.day_of_year)
        df["weekday"] = df.timestamp.apply(lambda dt: dt.weekday())

        df["geometry"] = df.apply(
            lambda row: Point([row.LON, row.LAT]), axis=1)
        gdf = GeoDataFrame(df, crs="epsg:4326").to_crs(ocrs)

        if model is not None:
            # Global Horizontal Irradiance (GHI) is the total amount of
            # shortwave radiation received from above by a surface
            # horizontal to the ground.

            # CONVERT GLO [J/cm2] -> GHI [W/m2]
            # rayonnement global horaire en heure UTC (en J/cm2)
            # gdf["GHI"] = (1e4/3600) * gdf.GLO

            # CONVERT GLO2 [J/cm2] -> GHI [W/m2]
            # rayonnement global horaire en heure TSV (en J/cm2)
            gdf["GHI"] = (1e4/3600) * gdf.GLO2

            # DETERMINE ZENITH ANGLES
            sunModel = SunLib(gdf, model=model)
            gdf["solar_alti"], gdf["solar_azim"] = gdf.apply(
                lambda row: sunModel.getSolarAnglesInDegrees(row.timestamp),
                axis=1, result_type="expand").to_numpy().transpose()

            gdf["sun_beam_dir"] = gdf.timestamp.apply(
                lambda dt: sunModel.getRadiationDirection(dt))
            if encode:
                gdf.sun_beam_dir = gdf.sun_beam_dir.apply(
                    lambda t: ArrayCoding.encode(t))

            gdf["solar_zenith"] = gdf.solar_alti.apply(
                lambda alti: 90-alti if (0 < alti) else 0)

            # Direct Normal Irradiance (DNI) is the amount of solar radiation
            # received per unit area by a surface that is always held perpendicular
            # (or normal) to the rays that come in a straight line from the
            # direction of the sun at its current position in the sky.

            # DETERMINE DNI FROM GHI USING THE DIRINT MODIF. OF THE DISC MODEL
            gdf.set_index("timestamp", drop=False, inplace=True)
            gdf["DNI"] = dirint(gdf.GHI, gdf.solar_zenith, gdf.index,
                                pressure=100*gdf.PSTAT,
                                use_delta_kt_prime=True,
                                temp_dew=gdf.TD,
                                min_cos_zenith=0.065,
                                max_zenith=87)

            gdf["cos_solar_zenith"] = (pi/180) * gdf.solar_zenith
            gdf.cos_solar_zenith = cos(gdf.cos_solar_zenith)

            # Diffuse Horizontal Irradiance (DHI) is the amount of radiation
            # received per unit area by a surface (not subject to any shade or
            # shadow) that does not arrive on a direct path from the sun, but
            # has been scattered by molecules and particles in the atmosphere
            # and comes equally from all directions

            # GHI = DNI x cos(theta) + DHI
            gdf["DHI"] = gdf.apply(lambda row: row.GHI -
                                   row.cos_solar_zenith*row.DNI, axis=1)

            gdf.drop(columns=["solar_zenith",
                     "cos_solar_zenith"], inplace=True)
            gdf.reset_index(drop=True, inplace=True)

        return gdf

    @staticmethod
    def _process(params):
        ifile, station, tzinfo, ocrs, model, encode = params
        df = MeteoFranceReader.__read(ifile, station, tzinfo)
        gdf = MeteoFranceReader.__enrich(df, ocrs, model, encode)
        return gdf

    def run(self):
        # PREPROCESS
        listOfParams = [
            (ifile, self.station, self.tzinfo, self.ocrs, self.model, self.encode)
            for ifile in self.ifiles
        ]

        # PROCESS
        pool = Pool()
        gdfs = pool.map(MeteoFranceReader._process, listOfParams)
        pool.close()

        # POSTPROCESS
        gdf = concat(gdfs, ignore_index=True)
        gdf.sort_values(by="timestamp", ascending=True, ignore_index=True,
                        inplace=True)
        return gdf


"""
PERIODS = [ (1900 + i, 1909 + i) for i in range(40, 120, 10) ] + [ (2020, 2022), (2023, 2024) ]
PERIODS = [ (2020, 2022), (2023, 2024) ]

rootdir = "/home/tleduc/data/meteofrance/data"
ifiles = [
    f"{rootdir}/HOR_departement_44_periode_{year0}-{year1}.csv"
    for year0, year1 in PERIODS
]
gdf = MeteoFranceReader(ifiles, station="NANTES-BOUGUENAIS").execute()

_gdf = gdf.loc[gdf[(gdf.day_of_year.isin([5, 6])) & (gdf.year == 2020)].index]

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
ax.plot(_gdf.timestamp, _gdf.DNI, color="blue", label="DNI")
ax.plot(_gdf.timestamp, _gdf.DHI, color="red", label="DHI")
ax.plot(_gdf.timestamp, _gdf.GHI, color="green", label="GHI")
ax.legend()
plt.savefig("DNI_DHI_GHI.pdf", bbox_inches="tight")
plt.show()
plt.close(fig)
"""
