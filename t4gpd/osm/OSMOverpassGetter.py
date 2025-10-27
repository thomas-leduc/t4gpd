"""
Created on 21 Jul. 2025

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

import warnings
from geopandas import GeoDataFrame
from numpy import ndarray
from overpy import Overpass, Way
from shapely import LineString, MultiPolygon, Point, Polygon, box
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils


class OSMOverpassGetter(GeoProcess):
    """
    classdocs
    """

    __slots__ = ("bbox", "type", "clip")
    TIMEOUT = 60  # Overpass timeout in seconds

    def __init__(self, bbox, type="buildings", clip=False):
        """
        Constructor
        """
        warnings.formatwarning = WarnUtils.format_Warning_alt
        if isinstance(bbox, GeoDataFrame):
            bbox = bbox.to_crs("EPSG:4326").total_bounds
        if isinstance(bbox, (list, ndarray, tuple)) and len(bbox) == 4:
            self.bbox = bbox
        else:
            raise IllegalArgumentTypeException(
                bbox, "GeoDataFrame or a list or tuple of 4 coordinates"
            )

        types = ("buildings", "pois", "roads", "streetlights", "trees", "wetlands")
        if type not in types:
            types = "', '".join(types)
            raise IllegalArgumentTypeException(type, f"'{types}'")
        self.type = type
        self.clip = clip

    @staticmethod
    def __buildings_querystring(south, west, north, east):
        # See https://overpass-turbo.eu/
        return f"""
[out:json][timeout:{OSMOverpassGetter.TIMEOUT}];
(
way["building"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""

    @staticmethod
    def __holed_buildings_querystring(south, west, north, east):
        # See https://overpass-turbo.eu/
        return f"""
[out:json][timeout:{OSMOverpassGetter.TIMEOUT}];
(
relation["building"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""

    @staticmethod
    def __holed_wetlands_querystring(south, west, north, east):
        # See https://overpass-turbo.eu/
        return f"""
[out:json][timeout:{OSMOverpassGetter.TIMEOUT}];
(
relation["amenity"="fountain"]({south},{west},{north},{east});
relation["landuse"="basin"]({south},{west},{north},{east});
relation["natural"="water"]["water"="basin"]({south},{west},{north},{east});
relation["natural"="water"]["water"="river"]({south},{west},{north},{east});
relation["natural"="wetland"]({south},{west},{north},{east});
relation["waterway"="riverbank"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""

    @staticmethod
    def __pois_querystring(south, west, north, east):
        # See https://overpass-turbo.eu/
        return f"""
[out:json][timeout:{OSMOverpassGetter.TIMEOUT}];
(
node ["amenity"]({south},{west},{north},{east});
node ["shop"]({south},{west},{north},{east});
node ["tourism"]({south},{west},{north},{east});
node ["leisure"]({south},{west},{north},{east});
node ["historic"]({south},{west},{north},{east});
node ["office"]({south},{west},{north},{east});
node ["craft"]({south},{west},{north},{east});
);
out body;
"""

    @staticmethod
    def __roads_querystring(south, west, north, east):
        # See https://overpass-turbo.eu/
        return f"""
[out:json][timeout:{OSMOverpassGetter.TIMEOUT}];
(
way["highway"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""

    @staticmethod
    def __streetlights_querystring(south, west, north, east):
        # See https://overpass-turbo.eu/
        return f"""
[out:json][timeout:{OSMOverpassGetter.TIMEOUT}];
(
node["highway"="street_lamp"]({south},{west},{north},{east});
node["man_made"="street_lamp"]({south},{west},{north},{east});
);
out body;
"""

    @staticmethod
    def __trees_querystring(south, west, north, east):
        # See https://overpass-turbo.eu/
        return f"""
[out:json][timeout:{OSMOverpassGetter.TIMEOUT}];
(
node["natural"="tree"]({south},{west},{north},{east});
);
out body;
"""

    @staticmethod
    def __wetlands_querystring(south, west, north, east):
        # See https://overpass-turbo.eu/
        return f"""
[out:json][timeout:{OSMOverpassGetter.TIMEOUT}];
(
way["amenity"="fountain"]({south},{west},{north},{east});
way["landuse"="basin"]({south},{west},{north},{east});
way["natural"="water"]({south},{west},{north},{east});
way["natural"="wetland"]({south},{west},{north},{east});
way["waterway"="riverbank"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""

    @staticmethod
    def __to_rows_of_linestrings(result, columns):
        warnings.warn(f"Traitement de {len(result.ways)} objets...")
        rows = []
        for way in result.ways:
            points = [(float(node.lon), float(node.lat)) for node in way.nodes]
            geometry = LineString(points)
            row = {"geometry": geometry, "id": way.id}
            row.update({col: way.tags.get(col) for col in columns})
            rows.append(row)
        return rows

    @staticmethod
    def __to_rows_of_multipolygons(result, result2, columns):
        rows = []

        # EMPRISES POLYGONALES NON TROUEES
        warnings.warn(f"Traitement de {len(result.ways)} objets...")

        for way in result.ways:
            points = [(float(node.lon), float(node.lat)) for node in way.nodes]
            # Parfois les polygones ne sont pas fermés : on ferme manuellement
            if points[0] != points[-1]:
                points.append(points[0])
            geometry = Polygon(points)
            row = {"geometry": geometry, "id": way.id}
            row.update({col: way.tags.get(col) for col in columns})
            rows.append(row)

        # EMPRISES POLYGONALES TROUEES OU MULTIPOLYGONALES
        if 0 < len(result.ways):
            warnings.warn(f"Traitement de {len(result2.relations)} relations...")

            for rel in result2.relations:
                outers = []
                inners = []
                for member in rel.members:
                    if not isinstance(member.resolve(), Way):
                        continue
                    points = [
                        (float(n.lon), float(n.lat)) for n in member.resolve().nodes
                    ]
                    if points[0] != points[-1]:
                        points.append(points[0])
                    if member.role == "outer":
                        outers.append(points)
                    elif member.role == "inner":
                        inners.append(points)

                # Créer le polygone avec trous
                if outers:
                    outer_polygons = []
                    for outer in outers:
                        polygon = Polygon(
                            outer,
                            holes=[
                                hole
                                for hole in inners
                                if Polygon(hole).within(Polygon(outer))
                            ],
                        )
                        outer_polygons.append(polygon)
                    geometry = (
                        MultiPolygon(outer_polygons)
                        if len(outer_polygons) > 1
                        else outer_polygons[0]
                    )
                    row = {"geometry": geometry, "id": way.id}
                    row.update({col: way.tags.get(col) for col in columns})
                    rows.append(row)

        return rows

    @staticmethod
    def __to_rows_of_points(result, columns):
        warnings.warn(f"Traitement de {len(result.nodes)} objets...")
        rows = []
        for node in result.nodes:
            geometry = Point((float(node.lon), float(node.lat)))
            row = {"geometry": geometry, "id": node.id}
            row.update({col: node.tags.get(col) for col in columns})
            rows.append(row)
        return rows

    @staticmethod
    def __overpass_query(bbox, type):
        # minx, miny, maxx, maxy = bbox
        west, south, east, north = bbox
        match type:
            case "buildings":
                query = OSMOverpassGetter.__buildings_querystring(
                    south, west, north, east
                )
            case "pois":
                query = OSMOverpassGetter.__pois_querystring(south, west, north, east)
            case "roads":
                query = OSMOverpassGetter.__roads_querystring(south, west, north, east)
            case "trees":
                query = OSMOverpassGetter.__trees_querystring(south, west, north, east)
            case "streetlights":
                query = OSMOverpassGetter.__streetlights_querystring(
                    south, west, north, east
                )
            case "wetlands":
                query = OSMOverpassGetter.__wetlands_querystring(
                    south, west, north, east
                )
            case _:
                raise IllegalArgumentTypeException(f"Unsupported type: {type}")

        api = Overpass()
        warnings.warn("Envoi de la requête Overpass...")
        result = api.query(query)
        rows = []
        match type:
            case "buildings":
                columns = ["barrier", "building", "height", "name", "source"]

                query2 = OSMOverpassGetter.__holed_buildings_querystring(
                    south, west, north, east
                )
                result2 = api.query(query2)

                rows = OSMOverpassGetter.__to_rows_of_multipolygons(
                    result, result2, columns
                )

            case "pois":
                columns = [
                    "amenity",
                    "shop",
                    "tourism",
                    "leisure",
                    "historic",
                    "office",
                    "craft",
                    "name",
                    "description",
                    # "website",
                    # "phone",
                    # "email",
                    # "addr:street",
                    # "addr:housenumber",
                    # "addr:city",
                    # "addr:postcode",
                    # "addr:country",
                    # "addr:full",
                    # "source",
                    # "operator",
                    # "wheelchair",
                    # "opening_hours",
                    # "capacity",
                    # "capacity:disabled",
                    # "capacity:parent",
                    # "capacity:child",
                    # "capacity:senior",
                    # "capacity:family",
                    # "capacity:staff",
                    # "capacity:total",
                    # "capacity:private",
                    # "capacity:public",
                    # "capacity:reserved",
                    # "capacity:reserved:disabled",
                    # "capacity:reserved:parent",
                    # "capacity:reserved:child",
                    # "capacity:reserved:senior",
                    # "capacity:reserved:family",
                    # "capacity:reserved:staff",
                    # "capacity:reserved:total",
                    # "capacity:reserved:private",
                    # "capacity:reserved:public",
                ]
                rows = OSMOverpassGetter.__to_rows_of_points(result, columns)

            case "roads":
                columns = [
                    "name",
                    "highway",
                    "surface",
                    "oneway",
                    "maxspeed",
                    "lanes",
                    "width",
                    "bridge",
                    "tunnel",
                ]
                rows = OSMOverpassGetter.__to_rows_of_linestrings(result, columns)

            case "streetlights":
                columns = [
                    "lamp_type",
                    "height",
                    "material",
                    "colour",
                ]
                rows = OSMOverpassGetter.__to_rows_of_points(result, columns)

            case "trees":
                columns = [
                    "species",
                    "height",
                    "circumference",
                    "leaf_cycle",
                    "leaf_type",
                ]
                rows = OSMOverpassGetter.__to_rows_of_points(result, columns)

            case "wetlands":
                columns = [
                    "natural",
                    "wetland",
                    "name",
                    "protection_title",
                    "protection_class",
                    "source",
                ]

                query2 = OSMOverpassGetter.__holed_wetlands_querystring(
                    south, west, north, east
                )
                result2 = api.query(query2)

                rows = OSMOverpassGetter.__to_rows_of_multipolygons(
                    result, result2, columns
                )

        if not rows:
            warnings.warn("Aucun résultat trouvé pour cette requête Overpass.")
            return GeoDataFrame(
                columns=["geometry", "id"] + list(columns), crs="EPSG:4326"
            )
        return GeoDataFrame(
            rows,
            crs="EPSG:4326",
        )

    def run(self):
        gdf = OSMOverpassGetter.__overpass_query(self.bbox, self.type)
        if self.clip:
            # Clip to the bounding box
            gdf = gdf.clip(box(*self.bbox))
        return gdf

    @staticmethod
    def test(usecase="ensan", clip=False):
        import matplotlib.pyplot as plt

        if usecase == "ensan":
            from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

            bbox = GeoDataFrameDemos.ensaNantesBuildings()
            # from t4gpd.demos.NantesBDT import NantesBDT
            # bbox = NantesBDT.buildings()

        else:
            # Coordonnées de la ville d'Avignon
            south, west, north, east = 43.94025, 4.788114, 43.956126, 4.825002
            bbox = (west, south, east, north)

        buildings, pois, roads, streetlights, trees, wetlands = (
            None,
            None,
            None,
            None,
            None,
            None,
        )

        buildings = OSMOverpassGetter(bbox, type="buildings", clip=clip).run()
        pois = OSMOverpassGetter(bbox, type="pois", clip=clip).run()
        roads = OSMOverpassGetter(bbox, type="roads", clip=clip).run()
        streetlights = OSMOverpassGetter(bbox, type="streetlights", clip=clip).run()
        trees = OSMOverpassGetter(bbox, type="trees", clip=clip).run()
        wetlands = OSMOverpassGetter(bbox, type="wetlands", clip=clip).run()

        fig, ax = plt.subplots(figsize=(1.75 * 8.26, 1.2 * 8.26))
        if buildings is not None and not buildings.empty:
            buildings.plot(ax=ax, color="lightgrey", edgecolor="black")
        if pois is not None and not pois.empty:
            pois.plot(ax=ax, color="blue", marker="P", label="OSM POIs")
        if usecase == "ensan":
            bbox.to_crs("epsg:4326").boundary.plot(
                ax=ax, edgecolor="red", linewidth=1, label="BD Topo"
            )
        if roads is not None and not roads.empty:
            roads.plot(ax=ax, color="black", label="OSM roads")
        if streetlights is not None and not streetlights.empty:
            streetlights.plot(ax=ax, color="yellow", label="OSM streetlights")
        if trees is not None and not trees.empty:
            trees.plot(ax=ax, color="green", label="OSM trees")
        if wetlands is not None and not wetlands.empty:
            wetlands.plot(ax=ax, color="blue")
        ax.axis("off")
        ax.legend(loc="lower right", fontsize=10)
        fig.tight_layout()
        plt.show()

        return buildings, pois, roads, streetlights, trees, wetlands


# buildings, pois, roads, streetlights, trees, wetlands = OSMOverpassGetter.test(
#     usecase="ensan", clip=True
# )
# buildings, pois, roads, streetlights, trees, wetlands = OSMOverpassGetter.test(
#     usecase="avignon", clip=False
# )
