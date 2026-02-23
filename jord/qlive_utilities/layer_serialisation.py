from typing import Any

APPEND_TIMESTAMP = True
SKIP_MEMORY_LAYER_CHECK_AT_CLOSE = True
PIXEL_SIZE = 1
DEFAULT_NUMBER = 0
CONTRAST_ENHANCE = True
DEFAULT_LAYER_NAME = "TemporaryLayer"
DEFAULT_LAYER_CRS = "EPSG:4326"
VERBOSE = False

__all__ = [
    "serialise_qgis_layer",
]


def serialise_qgis_layer(qgis_instance_handle: Any, layer: Any) -> None:
    """
      https://qgis.org/pyqgis/3.28/core/QgsJsonUtils.html#qgis.core.QgsJsonUtils.exportAttributes

      https://qgis.org/pyqgis/3.28/core/QgsJsonExporter.html


          asGeometryCollection

    Returns contents of the geometry as a list of geometries

    asJson

    Exports the geometry to a GeoJSON string.

    asMultiPoint

    Returns the contents of the geometry as a multi-point.

    asMultiPolygon

    Returns the contents of the geometry as a multi-polygon.

    asMultiPolyline

    Returns the contents of the geometry as a multi-linestring.

    asPoint

    Returns the contents of the geometry as a 2-dimensional point.

    asPolygon

    Returns the contents of the geometry as a polygon.

    asPolyline

    Returns the contents of the geometry as a polyline.

    asQPointF

    Returns contents of the geometry as a QPointF if wkbType is WKBPoint, otherwise returns a null QPointF.

    asQPolygonF

    Returns contents of the geometry as a QPolygonF.

    asWkb

    Export the geometry to WKB

    asWkt

    Exports the geometry to WKT


    TODO: Figure this

          :param qgis_instance_handle:
          :param layer:
          :return:
    """

    from qgis.core import QgsVectorLayer, QgsJsonExporter

    assert isinstance(layer, QgsVectorLayer)

    # geom_geojson_rep = layer.asJson(precision=17)
    layer_geojson_rep = QgsJsonExporter(
        layer, precision=17
    )  # Note that geometries will be automatically reprojected to WGS84 to match GeoJSON spec if either
    # the source vector layer or source CRS is set.

    return layer_geojson_rep


if __name__ == "__main__":
    print("A")
