from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Type, Union

import shapely
from osgeo import ogr

from .spatial_reference import get_spatial_reference_from_epsg

__all__ = [
    "create_ogr_table",
    "insert_ogr_table",
    "ShapelyGeometry",
    "FIELDS_TYPES_MAP",
    "OgrGeometryTypeEnum",
]


class OgrGeometryTypeEnum(Enum):
    point = ogr.wkbPoint
    line_string = ogr.wkbLineString
    polygon = ogr.wkbPolygon


FIELDS_TYPES_MAP = {  # https://gis.stackexchange.com/questions/18715/mapping-between-ogr-and-python-data-types
    int: ogr.OFTInteger,  # Simple 32bit integer
    float: ogr.OFTReal,  # Double Precision floating point
    str: ogr.OFTString,  # String of ASCII chars
}


@dataclass
class ShapelyGeometry:
    geometry: shapely.geometry.base.BaseGeometry


def create_ogr_table(
    spatialite_db: Path,
    table_name: str,
    fields: list[tuple[str, Type[Union[int, float, str]]]],
    srs_id: int,
) -> None:
    """

    :param spatialite_db: The spatialite_db to create table in
    :param table_name:
    :param fields: A list of fields to create in the table. Each field is a tuple defined as ("column_name",
    Type)
    :param srs_id: Spatial reference system id of the geometries.
    :return:
    """
    sqlite_dr = ogr.GetDriverByName("SQLite")
    sl_ds = sqlite_dr.Open(str(spatialite_db), update=1)
    sl_lyr = sl_ds.CreateLayer(
        table_name,
        srs=get_spatial_reference_from_epsg(srs_id),
        geom_type=OgrGeometryTypeEnum.polygon.value,
    )

    for field in fields:
        sl_lyr.CreateField(ogr.FieldDefn(field[0], FIELDS_TYPES_MAP[field[1]]))

    del sl_ds  # clean up


def insert_ogr_table(
    spatialite_db: Path, geoms: list[ShapelyGeometry], table_name: str
) -> None:
    """
    Inserts a list of ShapelyGeometry into table.

    :param spatialite_db:
    :param geoms:
    :param table_name:
    :return:
    """
    sl_ds = ogr.Open(str(spatialite_db), update=1)
    sl_lyr = sl_ds.GetLayerByName(table_name)

    feature_def = sl_lyr.GetLayerDefn()

    sl_lyr.StartTransaction()

    for g in geoms:
        geom = ogr.CreateGeometryFromWkb(g.geometry.wkb)
        geom.FlattenTo2D()

        dst_feat = ogr.Feature(feature_def)
        dst_feat.SetGeometryDirectly(geom)
        fields = g.__dict__
        fields.pop("geometry")
        for (
            field,
            value,
        ) in (
            fields.items()
        ):  # Add all fields - 'geometry' in SpacePolygon to the feature
            dst_feat.SetField(field, value)

        sl_lyr.CreateFeature(dst_feat)
        dst_feat = geom = None  # destroy these

    sl_lyr.CommitTransaction()
    del sl_ds
