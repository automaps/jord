__author__ = "heider"
__doc__ = r"""

           Created on 5/5/22
           """

from typing import Dict

from geopandas import GeoDataFrame

from jord.shapely_utilities import ShapelyGeometryTypesEnum

__all__ = ["split_on_geom_type"]


def split_on_geom_type(
    data_frame: GeoDataFrame,
) -> Dict[ShapelyGeometryTypesEnum, GeoDataFrame]:
    """options for filtering geometries in GeoDataFrame's, rather messy interface tbh, just like pandas.

    gdf0 = gdf.loc[gdf.geometry.geometry.type=='MultiPolygon']

    gdf1 = gdf[gdf.geometry.apply(lambda x : x.type=='MultiPolygon')]

    gdf2 = gdf[gdf.geom_type=='MultiPolygon']

    gdf3 = gdf[gdf.geometry.type=="MultiPolygon"]
    """
    return {
        t: data_frame[data_frame.geom_type == t.value.__name__]
        for t in ShapelyGeometryTypesEnum
    }
