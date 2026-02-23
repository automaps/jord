from enum import Enum

__all__ = [
    "VectorGeometryTypeEnum",
    "CommonCoordinateReferenceSystemEnum",
    "FieldTypeEnum",
]


class QgisWkbToVectorGeometryType(Enum): ...  # QgsWkbTypes.LineGeometry


class VectorGeometryTypeEnum(Enum):
    point = "point"  # ESRI shapefile
    line_string = "linestring"  # ESRI shapefile
    polygon = "polygon"  # ESRI shapefile
    multi_point = "multipoint"  # ESRI shapefile
    multi_line_string = "multilinestring"  # + Geopackage
    multi_polygon = "multipolygon"  # + Geopackage


class CommonCoordinateReferenceSystemEnum(Enum):
    epsg4326 = "epsg:4326"  # WGS 84
    epsg3857 = "EPSG:3857"  # WGS 84 / Pseudo-Mercator"


class FieldTypeEnum(Enum):
    integer = "integer"
    double = "double"
    string = "string"


def construct_layer_uri() -> str:
    """

    :return:
    :rtype:
    """
    return "Point?crs=epsg:4326&field=id:integer&field=name:string(20)&index=yes"
