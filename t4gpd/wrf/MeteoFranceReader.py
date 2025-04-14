"""
Created on 12 jan. 2024

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
from datetime import timedelta
from geopandas import GeoDataFrame
from pandas import concat, merge, read_csv, to_datetime
from shapely import Point
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.sun.SunModel import SunModel


class MeteoFranceReader(GeoProcess):
    """
    classdocs

    Données climatologiques de base - horaires
    https://meteo.data.gouv.fr/datasets/donnees-climatologiques-de-base-horaires
    """

    def __init__(
        self,
        ifiles,
        station=None,
        tzinfo="UTC",
        ocrs="epsg:2154",
        model="pvlib",
        version=2,
    ):
        """
        Constructor
        """
        self.ifiles = ifiles
        self.station = station
        # DEBUG DU 17.01.2024 :
        # Les releves des stations MeteoFrance sont en temps UTC
        self.tzinfo = tzinfo
        self.ocrs = ocrs
        self.model = model
        self.version = version

    @staticmethod
    def __read(ifile, station, tzinfo):
        df = read_csv(ifile, decimal=".", encoding="utf8", sep=";", nrows=None)
        if station is not None:
            df = df.query(f"NOM_USUEL == '{station}'").copy(deep=True)

        df["timestamp"] = to_datetime(
            df.AAAAMMJJHH, format="%Y%m%d%H", utc=False
        ).dt.tz_localize(tzinfo)

        df.rename(columns={col: col.strip() for col in df.columns}, inplace=True)
        df.reset_index(drop=True, inplace=True)
        # REMOVE EMPTY COLUMNS
        # df.dropna(axis=1, inplace=True, how="all")
        return df

    @staticmethod
    def __enrich(df, ocrs, model, version):
        # DEBUG DU 17.01.2024 :
        # LE CHAMP GLO2 EST SYSTÉMATIQUEMENT RENSEIGNE... CONTRAIREMENT
        # AU CHAMP GLO (QUI NE L'EST QUE DEPUIS LES ANNÉES 2000)
        # GLO2 = rayonnement global horaire en heure TSV (en J/cm2)
        # TSV = Temps Solaire Vrai (Apparent solar time or true solar time)
        longitude = df.at[0, "LON"] if (0 < len(df)) else None
        df["timestamp2"] = df.timestamp.apply(
            lambda dt: dt + timedelta(hours=(longitude * 12 / 180))
        )

        df["year"] = df.timestamp.apply(lambda dt: dt.year)
        df["month"] = df.timestamp.apply(lambda dt: dt.month)
        df["day"] = df.timestamp.apply(lambda dt: dt.day)
        df["hour"] = df.timestamp.apply(lambda dt: dt.hour)
        df["day_of_year"] = df.timestamp.apply(lambda dt: dt.day_of_year)
        df["weekday"] = df.timestamp.apply(lambda dt: dt.weekday())

        df["geometry"] = df.apply(lambda row: Point([row.LON, row.LAT]), axis=1)
        gdf = GeoDataFrame(df, crs="epsg:4326").to_crs(ocrs)

        if (model is not None) and (longitude is not None):
            # Global Horizontal Irradiance (GHI) is the total amount of
            # shortwave radiation received from above by a surface
            # horizontal to the ground.

            # Direct Normal Irradiance (DNI) is the amount of solar radiation
            # received per unit area by a surface that is always held perpendicular
            # (or normal) to the rays that come in a straight line from the
            # direction of the sun at its current position in the sky.

            # Diffuse Horizontal Irradiance (DHI) is the amount of radiation
            # received per unit area by a surface (not subject to any shade or
            # shadow) that does not arrive on a direct path from the sun, but
            # has been scattered by molecules and particles in the atmosphere
            # and comes equally from all directions

            # GHI = DNI x cos(theta_zenith) + DHI

            # CONVERT GLO2 [J/cm2] -> GHI [W/m2]
            # rayonnement global horaire en heure TSV (en J/cm2)
            gdf["GHI"] = (1e4 / 3600) * gdf.GLO2

            # DETERMINE ZENITH ANGLES
            sunModel = SunModel(gdf, altitude=0, model=model)
            sim = sunModel.positions_clearsky_irradiances_and_sun_beam_direction(
                gdf.timestamp2
            )
            if 1 == version:
                sim = sim.loc[
                    :,
                    [
                        "apparent_elevation",
                        "azimuth",
                        "sun_beam_direction",
                        "dni",
                        "dhi",
                    ],
                ].rename(
                    columns={
                        "apparent_elevation": "solar_alti",
                        "azimuth": "solar_azim",
                        "sun_beam_direction": "sun_beam_dir",
                        "dni": "DNI",
                        "dhi": "DHI",
                    }
                )
            else:
                sim.rename(
                    columns={col: f"{col}_{model}" for col in sim.columns}, inplace=True
                )

            gdf = merge(gdf, sim, left_on="timestamp2", right_index=True)

        gdf.drop(columns=["timestamp2"], inplace=True)
        return gdf

    def __process(self, ifile):
        df = MeteoFranceReader.__read(ifile, self.station, self.tzinfo)
        gdf = MeteoFranceReader.__enrich(df, self.ocrs, self.model, self.version)
        return gdf

    def run(self):
        # PROCESS
        gdfs = []
        for ifile in self.ifiles:
            gdfs.append(self.__process(ifile))

        # POSTPROCESS
        gdf = GeoDataFrame(concat(gdfs, ignore_index=True), crs=self.ocrs)
        gdf.sort_values(by="timestamp", ascending=True, ignore_index=True, inplace=True)
        gdf.reset_index(drop=True, inplace=True)
        return gdf


"""
PERIODS = [(1900 + i, 1909 + i) for i in range(40, 120, 10)] + [
    (2020, 2022),
    (2023, 2024),
]
PERIODS = [(2020, 2023), (2024, 2025)]
# PERIODS = [(2024, 2025)]

rootdir = "/home/tleduc/data/meteofrance/data"
ifiles = [
    f"{rootdir}/HOR_departement_44_periode_{year0}-{year1}.csv.gz"
    for year0, year1 in PERIODS
]
gdf = MeteoFranceReader(ifiles, station="NANTES-BOUGUENAIS").execute()

_gdf = gdf.loc[gdf[(gdf.day_of_year.isin([5, 6])) & (gdf.year == 2024)].index]

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
ax.plot(_gdf.timestamp, _gdf.dni_pvlib, color="blue", label="dni_pvlib")
ax.plot(_gdf.timestamp, _gdf.dhi_pvlib, color="red", label="dhi_pvlib")
ax.plot(_gdf.timestamp, _gdf.ghi_pvlib, color="green", label="ghi_pvlib")
ax.plot(_gdf.timestamp, _gdf.GHI, color="brown", linestyle="-.", label="GHI")
ax.legend()
plt.savefig("DNI_DHI_GHI.pdf", bbox_inches="tight")
plt.show()
plt.close(fig)
"""
