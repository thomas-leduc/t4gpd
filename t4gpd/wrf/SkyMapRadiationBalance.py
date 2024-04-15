'''
Created on 21 jan. 2024

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
from datetime import date, datetime, timedelta, timezone
from geopandas import GeoDataFrame
from numpy import cos, dot, ndarray
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.energy.PerrinDeBrichambaut import PerrinDeBrichambaut
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class SkyMapRadiationBalance(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, skymaps, dt, meteo=None, svfFieldname="svf",
                 anglesFieldname="angles", model="pysolar", encode=False):
        '''
        Constructor
        '''
        if not isinstance(skymaps, GeoDataFrame):
            raise IllegalArgumentTypeException(skymaps, "GeoDataFrame")
        self.skymaps = skymaps

        if not svfFieldname in skymaps:
            raise Exception(f"{svfFieldname} is not a relevant field name!")
        self.svf = svfFieldname

        if not anglesFieldname in skymaps:
            raise Exception(f"{anglesFieldname} is not a relevant field name!")
        self.angles = anglesFieldname

        sunModel = SunLib(gdf=skymaps, model=model)
        if isinstance(dt, datetime):
            day = date(*dt.timetuple()[0:3])
            dt0 = sunModel.getSunrise(day) + timedelta(hours=1)
            dt1 = dt
        elif isinstance(dt, date):
            dt0 = sunModel.getSunrise(dt) + timedelta(hours=1)
            dt1 = sunModel.getSunset(dt)
        elif (isinstance(dt, (list, ndarray, tuple)) and
              isinstance(dt[0], datetime) and isinstance(dt[1], datetime)):
            dt0, dt1 = dt
            if (date(*dt0.timetuple()[0:3]) != date(*dt1.timetuple()[0:3])):
                raise IllegalArgumentTypeException(
                    dt, "Pair of datetimes must occur on the same day!")
            if (dt0 > dt1):
                raise IllegalArgumentTypeException(
                    dt, "Pair of datetimes must be ordered!")
        else:
            raise IllegalArgumentTypeException(
                dt, "single date or datetime; or pair of datetimes")

        self.dts = [
            datetime(*dt0.timetuple()[0:3], h, tzinfo=timezone.utc)
            for h in range(dt0.hour, dt1.hour+1)
        ]

        if meteo is None:
            day = date(*self.dts[0].timetuple()[0:3])
            self.irrad = SkyMapRadiationBalance.__theoretical_irrad(
                sunModel, day)
        else:
            if "timestamp" in meteo:
                day = date(*self.dts[0].timetuple()[0:3])
                self.irrad = SkyMapRadiationBalance.__irrad_from_daily_meteo(
                    meteo, day)
            else:
                month = self.dts[0].month
                self.irrad = SkyMapRadiationBalance.__irrad_from_monthly_meteo(
                    meteo, month)
        self.encode = encode

    @staticmethod
    def __irrad_from_daily_meteo(meteo, day):
        cols = ["hour", "sun_beam_dir", "solar_alti",
                "solar_azim", "GHI", "DNI", "DHI",]
        _day = day.strftime("%Y%m%d")
        _meteo = meteo.loc[meteo[
            meteo.timestamp.apply(lambda dt: dt.strftime("%Y%m%d") == _day)
        ].index, cols]
        _meteo.set_index("hour", drop=True, inplace=True)
        return _meteo.to_dict(orient="index")

    @staticmethod
    def __irrad_from_monthly_meteo(meteo, month):
        cols = ["hour", "sun_beam_dir", "solar_alti",
                "solar_azim", "GHI", "DNI", "DHI"]
        _meteo = meteo.loc[meteo[meteo.month == month].index, cols]
        _meteo.set_index("hour", drop=True, inplace=True)
        return _meteo.to_dict(orient="index")

    @staticmethod
    def __theoretical_irrad(sunModel, day, skyType=PerrinDeBrichambaut.STANDARD_SKY):
        result = {}
        dt0 = datetime(*day.timetuple()[0:3], 0, tzinfo=timezone.utc)
        for h in range(24):
            dt = dt0 + timedelta(hours=h)
            alti, azim = sunModel.getSolarAnglesInDegrees(dt)
            sbdir = sunModel.getRadiationDirection(dt)
            dni, dhi, ghi = 0, 0, 0
            if (0.0 < alti):
                dni = PerrinDeBrichambaut.directNormalIrradiance(
                    AngleLib.toRadians(alti), skyType=skyType)
                dhi = PerrinDeBrichambaut.diffuseSolarIrradiance(
                    AngleLib.toRadians(alti), skyType)
                # GHI = DNI x cos(theta) + DHI
                ghi = dni * cos(AngleLib.toRadians(90-alti)) + dhi

            result[h] = {
                "sun_beam_dir": sbdir,
                "solar_alti": alti,
                "solar_azim": azim,
                "GHI": ghi,
                "DNI": dni,
                "DHI": dhi
            }
        return result

    @staticmethod
    def __in_direct_sunlight(angles, sunAlti, sunAzim):
        nangles = len(angles)
        offset = 360 / nangles
        position_in_vect = int((sunAzim + offset/2) / offset) % 64
        return 1 if (sunAlti > angles[position_in_vect]) else 0

    def runWithArgs(self, row):
        normal = (0, 0, 1)

        svf, angles = row[self.svf], row[self.angles]

        sw_direct, sw_diffuse = 0, 0
        beInTheSun = []

        for dt in self.dts:
            sunBeamDir, alti, azim, ghi, dni, dhi = self.irrad[dt.hour].values(
            )

            curr_beInTheSun = SkyMapRadiationBalance.__in_direct_sunlight(
                angles, alti, azim)
            beInTheSun.append(curr_beInTheSun)

            curr_sw_direct = curr_beInTheSun * dni * dot(sunBeamDir, normal)
            sw_direct += curr_sw_direct

            curr_sw_diffuse = svf * dhi
            sw_diffuse += curr_sw_diffuse

        hours_in_sunlight = sum(beInTheSun)
        hours_of_shade = len(beInTheSun) - hours_in_sunlight
        if self.encode:
            beInTheSun = ArrayCoding.encode(beInTheSun)
        return {
            "in_the_sun": beInTheSun,
            "hrs_in_sun": hours_in_sunlight,
            "hrs_shade": hours_of_shade,
            "sw_direct": sw_direct,
            "sw_diffuse": sw_diffuse,
            # "lw_atmos": lw_atmos,
            # "sum_sw_lw": sum_sw_lw,
        }


"""
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STSkyMap25D import STSkyMap25D
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.wrf.MeteoFrancePredictor import MeteoFrancePredictor
from t4gpd.wrf.MeteoFranceReader import MeteoFranceReader

buildings = GeoDataFrameDemos.ensaNantesBuildings()
sensors = STGrid(buildings, dx=80, dy=None, indoor=False,
    intoPoint=True, withDist=False).run() # < 0.1 sec.
skymaps = STSkyMap25D(buildings, sensors, nRays=64, rayLength=100,
	elevationFieldname="HAUTEUR", h0=0.0, size=1.0,
	withIndices=True, withAngles=True, encode=False).execute() # < 10 sec.

PERIODS = [
    # (2020, 2022),
    (2023, 2024),
]

rootdir = "/home/tleduc/data/meteofrance/data"
ifiles = [
    f"{rootdir}/HOR_departement_44_periode_{year0}-{year1}.csv"
    for year0, year1 in PERIODS
]
meteo = MeteoFranceReader(ifiles, station="NANTES-BOUGUENAIS").execute()
meteo2 = MeteoFrancePredictor(meteo).execute()

day = date(2023, 6, 21)
op = SkyMapRadiationBalance(skymaps, day, meteo=meteo2)
irrad1 = STGeoProcess(op, skymaps).run()

op = SkyMapRadiationBalance(skymaps, day, meteo=meteo)
irrad2 = STGeoProcess(op, skymaps).run()
"""

"""
import matplotlib.pyplot as plt
from pandas import read_csv, to_datetime
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STSkyMap25D import STSkyMap25D
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

buildings = GeoDataFrameDemos.ensaNantesBuildings()
sensors = STGrid(buildings, dx=80, dy=None, indoor=False,
                 intoPoint=True, withDist=False).run()  # < 0.1 sec.
skymaps = STSkyMap25D(buildings, sensors, nRays=64, rayLength=100,
                      elevationFieldname="HAUTEUR", h0=0.0, size=9.0,
                      withIndices=True, withAngles=True, encode=False).run()  # < 1 sec.

meteo = read_csv(
    "/home/tleduc/prj/spatial_distribution_of_solar_radiation/data/meteorology_extreme.csv")
meteo.timestamp = meteo.timestamp.apply(lambda dt: to_datetime(dt))
meteo.sun_beam_dir = meteo.sun_beam_dir.apply(lambda dt: ArrayCoding.decode(dt))

day = date(2022, 12, 22)
day = date(2022, 6, 13)
op = SkyMapRadiationBalance(skymaps, day, meteo=meteo)
irrad = STGeoProcess(op, skymaps).run()

fig, ax = plt.subplots(figsize=(1.0*8.26, 1.0*8.26))
buildings.plot(ax=ax)
# skymaps.plot(ax=ax, column="svf", legend=True, legend_kwds={"label": "svf"})
irrad.set_geometry("viewpoint").plot(ax=ax, column="hrs_in_sun", legend=True)
fig.tight_layout()
ax.axis("off")
plt.show()
"""

"""
import matplotlib.pyplot as plt
from pandas import read_csv, to_datetime
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STSkyMap25D import STSkyMap25D
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

buildings = GeoDataFrameDemos.ensaNantesBuildings()
sensors = STGrid(buildings, dx=80, dy=None, indoor=False,
                 intoPoint=True, withDist=False).run()  # < 0.1 sec.
skymaps = STSkyMap25D(buildings, sensors, nRays=64, rayLength=100,
                      elevationFieldname="HAUTEUR", h0=0.0, size=9.0,
                      withIndices=True, withAngles=True, encode=False).run()  # < 1 sec.

meteo = read_csv(
    "/home/tleduc/prj/spatial_distribution_of_solar_radiation/data/meteorology.csv")
meteo.sun_beam_dir = meteo.sun_beam_dir.apply(lambda dt: ArrayCoding.decode(dt))

day = date(2024, 3, 1)  # Focus on March
op = SkyMapRadiationBalance(skymaps, day, meteo=meteo)
irrad = STGeoProcess(op, skymaps).run()

fig, ax = plt.subplots(figsize=(1.0*8.26, 1.0*8.26))
buildings.plot(ax=ax)
# skymaps.plot(ax=ax, column="svf", legend=True, legend_kwds={"label": "svf"})
irrad.set_geometry("viewpoint").plot(ax=ax, column="sw_direct", legend=True)
fig.tight_layout()
ax.axis("off")
plt.show()
"""

"""
import matplotlib.pyplot as plt
from pandas import read_csv, to_datetime
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STSkyMap25D import STSkyMap25D
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

buildings = GeoDataFrameDemos.ensaNantesBuildings()
sensors = STGrid(buildings, dx=80, dy=None, indoor=False,
                 intoPoint=True, withDist=False).run()  # < 0.1 sec.
skymaps = STSkyMap25D(buildings, sensors, nRays=64, rayLength=100,
                      elevationFieldname="HAUTEUR", h0=0.0, size=9.0,
                      withIndices=True, withAngles=True, encode=False).run()  # < 1 sec.

day = date(2022, 6, 13)  # Focus on the hottest day
# day = date(2022, 12, 22)  # Focus on the coldest day
# irrad = SkyMapRadiationBalance2(skymaps, day, meteo=None).run()

meteo = read_csv(
    "/home/tleduc/prj/spatial_distribution_of_solar_radiation/data/meteorology_extreme.csv")
meteo.timestamp = meteo.timestamp.apply(lambda dt: to_datetime(dt))

# meteo = read_csv("/home/tleduc/prj/spatial_distribution_of_solar_radiation/data/meteorology.csv")
meteo.sun_beam_dir = meteo.sun_beam_dir.apply(lambda dt: ArrayCoding.decode(dt))

op = SkyMapRadiationBalance(skymaps, day, meteo=meteo)
irrad1 = STGeoProcess(op, skymaps).run()
print(irrad1[["gid", "svf", "in_the_sun", "hrs_in_sun", "hrs_shade", "sw_direct", "sw_diffuse"]])

fig, ax = plt.subplots(figsize=(1.0*8.26, 1.0*8.26))
buildings.plot(ax=ax)
irrad1.set_geometry("viewpoint").plot(ax=ax, column="sw_direct", legend=True)
irrad1.set_geometry("viewpoint").apply(lambda x: ax.annotate(
	text=x.gid, xy=x.geometry.centroid.coords[0],
	color="black", size=12, ha="center"), axis=1)
fig.tight_layout()
ax.axis("off")
plt.show()
plt.close(fig)
"""
