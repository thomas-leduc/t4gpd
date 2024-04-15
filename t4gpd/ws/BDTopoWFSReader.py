'''
Created on 17 oct. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from geopandas import clip, GeoDataFrame
from io import StringIO
from pandas import read_csv
from requests import get
from shapely.wkt import loads
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class BDTopoWFSReader(GeoProcess):
    '''
    classdocs
    '''
    URL = "https://wxs.ign.fr/topographie/geoportail/wfs"

    def __init__(self, roi, layer="batiment", clip=False, crs="EPSG:2154"):
        '''
        Constructor
        '''
        if not isinstance(roi, GeoDataFrame):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")

        self.roi = roi
        self.layer = layer
        self.clip = clip
        self.crs = crs

    @staticmethod
    def buildings(roi, clip=True, crs="EPSG:2154"):
        return BDTopoWFSReader(roi, layer="batiment", clip=clip, crs=crs).run()

    @staticmethod
    def listlayers():
        # https://geoservices.ign.fr/services-web-experts-topographie
        import re

        RE = re.compile(r"BDTOPO_V3:\w*")

        params = dict(
            request="GetCapabilities",
            service="WFS",
            version="2.0.0",
        )

        response = get(BDTopoWFSReader.URL, params=params)
        if (200 == response.status_code):
            html = response.content.decode(encoding="utf-8")
            html = RE.findall(html)
            html = sorted(list(set(html)))
            return html
        raise Exception(f"WFS error: {response.status_code}")

    def __get_features(self):
        minx, miny, maxx, maxy = self.roi.to_crs("EPSG:4326").total_bounds
        params = dict(
            # bbox="{0},{1},{2},{3}".format(*roi.total_bounds),
            bbox="{0},{1},{2},{3}".format(
                miny, minx, maxy, maxx),  # WARNING YX!
            # count=50,
            # filter="",
            # outputFormat="SHAPE-ZIP",
            outputFormat="csv",
            request="GetFeature",
            service="WFS",
            # startIndex=0,
            typeName=f"BDTOPO_V3:{self.layer}",
            version="2.0.0",
            srsname=self.crs,
            # srsname="urn:ogc:def:crs:EPSG::4326",
        )
        response = get(BDTopoWFSReader.URL, params=params)
        if (200 == response.status_code):
            csv = response.content.decode(encoding="utf-8")
            rows = StringIO(csv)
            df = read_csv(rows, decimal=".", sep=",")
            df.rename(columns={"geometrie": "geometry"}, inplace=True)
            df.geometry = df.geometry.apply(lambda g: loads(g))
            return GeoDataFrame(df, crs=self.crs)
        raise Exception(f"WFS error: {response.status_code}")

    @staticmethod
    def roads(roi, clip=True, crs="EPSG:2154"):
        return BDTopoWFSReader(roi, layer="troncon_de_route", clip=clip, crs=crs).run()

    def run(self):
        gdf = self.__get_features()
        if self.clip:
            gdf = clip(gdf, self.roi.total_bounds, keep_geom_type=True)
        return gdf


"""
import matplotlib.pyplot as plt
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

roi = GeoDataFrameDemos.ensaNantesBuildings()
buildings = BDTopoWFSReader.buildings(roi)
roads = BDTopoWFSReader.roads(roi)

# buildings = BDTopoWFSReader(roi, layer="batiment").run()
# roads = BDTopoWFSReader(roi, layer="troncon_de_route", clip=True).run()

fig, ax = plt.subplots(figsize=(8.26, 8.26))
roi.boundary.plot(ax=ax, color="red")
buildings.plot(ax=ax, color="grey")
roads.plot(ax=ax, color="black")
plt.show()

print(BDTopoWFSReader.listlayers())
"""
