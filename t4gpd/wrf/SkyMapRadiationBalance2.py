'''
Created on 27 mar. 2024

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
from numpy import asarray, cos, dot, heaviside, matmul, ndarray, repeat, stack, zeros
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.energy.PerrinDeBrichambaut import PerrinDeBrichambaut


class SkyMapRadiationBalance2(GeoProcess):
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
        elif (isinstance(dt, (list, ndarray, tuple)) and (2 == len(dt)) and
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
            self.irrad = SkyMapRadiationBalance2.__theoretical_irrad(
                sunModel, self.dts)
        else:
            if "timestamp" in meteo:
                self.irrad = SkyMapRadiationBalance2.__irrad_from_daily_meteo(
                    meteo, self.dts)
            else:
                self.irrad = SkyMapRadiationBalance2.__irrad_from_monthly_meteo(
                    meteo, self.dts)
        self.encode = encode

    @staticmethod
    def __irrad_from_daily_meteo(meteo, dts):
        cols = ["hour", "sun_beam_dir", "solar_alti",
                "solar_azim", "GHI", "DNI", "DHI",]
        _meteo = meteo.loc[meteo[
            (dts[0] <= meteo.timestamp) & (meteo.timestamp <= dts[-1])
        ].index, cols]
        _meteo.set_index("hour", drop=True, inplace=True)
        return _meteo.to_dict(orient="index")

    @staticmethod
    def __irrad_from_monthly_meteo(meteo, dts):
        cols = ["hour", "sun_beam_dir", "solar_alti",
                "solar_azim", "GHI", "DNI", "DHI"]
        month = dts[0].month
        h0, h1 = dts[0].hour, dts[-1].hour

        _meteo = meteo.loc[meteo[
            (meteo.month == month) & (meteo.hour.isin(range(h0, h1+1)))
        ].index, cols]
        _meteo.set_index("hour", drop=True, inplace=True)
        return _meteo.to_dict(orient="index")

    @staticmethod
    def __theoretical_irrad(sunModel, dts, skyType=PerrinDeBrichambaut.STANDARD_SKY):
        result = {}
        for dt in dts:
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

            result[dt.hour] = {
                "sun_beam_dir": sbdir,
                "solar_alti": alti,
                "solar_azim": azim,
                "GHI": ghi,
                "DNI": dni,
                "DHI": dhi
            }
        return result

    def run(self):
        hours = sorted(self.irrad.keys())
        nangles = len(self.skymaps.loc[self.skymaps.index.min(), self.angles])
        nhours, nsensors = len(hours), len(self.skymaps)

        # ========== DHI PRE-PROCESSING ==========
        dhi = asarray([self.irrad[h]["DHI"] for h in hours])
        dhi = dhi.sum()

        # ========== DNI PRE-PROCESSING ==========
        sunAzim = asarray([self.irrad[h]["solar_azim"] for h in hours])
        offset = 360 / nangles
        sunAzim = ((sunAzim + offset/2) / offset).astype(int) % 64
        delta = zeros([nangles, nhours])
        for c, l in enumerate(sunAzim):
            delta[l, c] = 1

        sunAlti = asarray([self.irrad[h]["solar_alti"] for h in hours])
        sunAlti = sunAlti.reshape(1, -1)
        sunAlti = repeat(sunAlti, nsensors, axis=0)
        sunAlti[sunAlti < 0] = 0

        M = stack(self.skymaps[self.angles].to_numpy())
        H = heaviside(sunAlti - matmul(M, delta), 0)
        H = H.astype(int)

        dniMagn = asarray([self.irrad[h]["DNI"] for h in hours])
        dni = asarray([self.irrad[h]["sun_beam_dir"] for h in hours])
        normal = (0, 0, 1)
        dni = dot(dni, normal)
        dni[dni < 0] = 0
        dni = dniMagn * dni

        dni = matmul(H, dni)

        # PROCESSING
        hrs_in_sun = H.sum(axis=1)
        result = self.skymaps.copy(deep=True)
        result["in_the_sun"] = H.tolist()
        result["hrs_in_sun"] = hrs_in_sun
        result["hrs_shade"] = nhours-hrs_in_sun
        result["sw_diffuse"] = dhi * result[self.svf]
        result["sw_direct"] = dni
        return result


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

irrad2 = SkyMapRadiationBalance2(skymaps, day, meteo=meteo).run()
print(irrad2[["gid", "svf", "in_the_sun", "hrs_in_sun", "hrs_shade", "sw_direct", "sw_diffuse"]])

fig, ax = plt.subplots(figsize=(1.0*8.26, 1.0*8.26))
buildings.plot(ax=ax)
irrad2.set_geometry("viewpoint").plot(ax=ax, column="sw_direct", legend=True)
irrad2.set_geometry("viewpoint").apply(lambda x: ax.annotate(
	text=x.gid, xy=x.geometry.centroid.coords[0],
	color="black", size=12, ha="center"), axis=1)
fig.tight_layout()
ax.axis("off")
plt.show()
plt.close(fig)
"""
