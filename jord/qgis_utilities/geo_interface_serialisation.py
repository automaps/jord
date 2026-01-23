import logging
import shapely

# noinspection PyUnresolvedReferences
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY
from shapely.geometry import shape
from typing import List, Union

from jord.shapely_utilities import is_multi

_logger = logging.getLogger(__name__)


def already_exist_question_mark(iface):
    layer = iface.activeLayer()
    feature = layer.selectedFeatures()[0]
    shape(feature.__geo_interface__["geometry"])
    shape(feature.geometry().__geo_interface__)


def monkey_patch():
    def mapping_feature(feature):
        geom = feature.geometry()

        properties = {}
        fields = [field.name() for field in feature.fields()]
        properties = dict(zip(fields, feature.attributes()))
        return {
            "type": "Feature",
            "properties": properties,
            "geometry": geom.__geo_interface__,
        }

    def mapping_geometry(geometry):
        geo = geometry.exportToGeoJSON()

        # We have to use eval because exportToGeoJSON() gives us
        # back a string that looks like a dictionary.
        return eval(geo)

    QgsFeature.__geo_interface__ = property(lambda self: mapping_feature(self))
    QgsGeometry.__geo_interface__ = property(lambda self: mapping_geometry(self))


def q_point_creation(
    shapely_geometry: shapely.geometry.base.BaseGeometry,
) -> Union[List[QgsPointXY], List[List[QgsPointXY]]]:
    """
    Construct a List of List or List of QgsPointXY objects.

    :return: Union[List[QgsPointXY], List[List[QgsPointXY]]]
    """

    assert not is_multi(shapely_geometry)

    points = []
    if isinstance(shapely_geometry, shapely.Polygon):
        exterior = []
        for coords in shapely_geometry.exterior.coords:
            points.append(QgsPointXY(*coords))
        points.append(exterior)

        for interior in shapely_geometry.interiors:
            interior_coords = []
            for coords in interior.coords:
                interior_coords.append(QgsPointXY(*coords))
            points.append(interior_coords)

    else:
        for coords in shapely_geometry.coords:
            points.append(QgsPointXY(*coords))

    return points


def q_point_geometry_creation(
    shapely_geometry: shapely.geometry.base.BaseGeometry,
) -> QgsGeometry:
    """
      QgsGeometry object from a basis of QgsPointXY objects.


    fromMultiPointXY	Creates a new geometry from a QgsMultiPointXY object
    fromMultiPolygonXY	Creates a new geometry from a QgsMultiPolygon
    fromMultiPolylineXY	Creates a new geometry from a QgsMultiPolylineXY object
    fromPointXY	Creates a new geometry from a QgsPointXY object
    fromPolygonXY	Creates a new geometry from a QgsPolygon
    fromPolylineXY	Creates a new LineString geometry from a list of QgsPointXY points.

      :return: QgsFeature
    """

    geom = None

    if is_multi(shapely_geometry):
        point_geoms = []
        for geom in shapely_geometry.geoms:
            point_geoms.append(q_point_creation(geom))

        if isinstance(shapely_geometry, shapely.MultiPoint):
            geom = QgsGeometry.fromMultiPointXY(point_geoms)
        elif isinstance(shapely_geometry, shapely.MultiLineString):
            geom = QgsGeometry.fromMultiPolylineXY(point_geoms)
        elif isinstance(shapely_geometry, shapely.MultiPolygon):
            geom = QgsGeometry.fromMultiPolygonXY(point_geoms)
        else:
            _logger.error(f"Geometry type {type(shapely_geometry)} is not supported")

    else:
        point_geom = q_point_creation(shapely_geometry)

        if isinstance(shapely_geometry, shapely.Point):
            geom = QgsGeometry.fromPointXY(point_geom)
        elif isinstance(shapely_geometry, shapely.LineString):
            geom = QgsGeometry.fromPolylineXY(point_geom)
        elif isinstance(shapely_geometry, shapely.Polygon):
            geom = QgsGeometry.fromPolygonXY(point_geom)
        else:
            _logger.error(f"Geometry type {type(shapely_geometry)} is not supported")

    return geom


def q_point_feature_creation(
    shapely_geometry: shapely.geometry.base.BaseGeometry,
) -> QgsFeature:
    """
    A QgsFeature object from a QgsGeometry object from a basis of QgsPointXY objects.


    :return: QgsFeature
    """

    feat = QgsFeature()
    feat.setGeometry(q_point_geometry_creation(shapely_geometry))
    return feat
