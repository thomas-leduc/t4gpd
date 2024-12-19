'''
Created on 3 dec. 2024

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
from geopandas import GeoDataFrame
from pandas import DatetimeIndex, concat
from pvlib.location import Location
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib


class PvlibProxy(object):
    '''
    classdocs
    '''
    @staticmethod
    def get_ghi_dni_dhi_positions(gdf, dtFieldname, altitude=0, model="ineichen"):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if not dtFieldname in gdf:
            raise IllegalArgumentTypeException(
                dtFieldname, "is not a valid timestamp field name")

        lat, lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        location = Location(lat, lon, altitude)

        dts = DatetimeIndex(gdf[dtFieldname])
        clear_sky = location.get_clearsky(dts, model=model)
        solar_position = location.get_solarposition(dts)

        result = concat([clear_sky, solar_position], axis=1)
        result.reset_index(names="timestamp", inplace=True)
        # result = result.loc[:, ["timestamp", "ghi", "dni", "dhi",
        #                         "apparent_elevation", "azimuth"]]

        return result

    @staticmethod
    def append_ghi_dni_dhi_positions(gdf, dtFieldname, altitude=0, model="ineichen"):
        clearsky = PvlibProxy.get_ghi_dni_dhi_positions(
            gdf, dtFieldname, altitude, model)
        result = gdf.merge(clearsky, how="inner", on=dtFieldname)
        return result


"""
from t4gpd.picoclim.PicopattReader import PicopattReader

inputFile = "/media/tleduc/disk_20241128/uclimweb/data/picopatt_nantes/picopatt_nantes*loire*20240919*1829.csv"
# inputFile = "/media/tleduc/disk_20241128/uclimweb/data/picopatt_montpellier/picopatt_montpellier*antigone*20240710*1412.csv"
df = PicopattReader(inputFile).run()
df2 = PvlibProxy.append_ghi_dni_dhi_positions(df, "timestamp")
print(df.head(3))
print(df2.head(3))
"""
