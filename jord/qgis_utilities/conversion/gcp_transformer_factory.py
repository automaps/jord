import logging
from pathlib import Path
from typing import Any

from qgis._core import QgsVectorLayer
from qgis.analysis import QgsGcpGeometryTransformer, QgsGcpTransformerInterface
from qgis.core import Qgis, QgsLayerTreeLayer, QgsPointXY

__all__ = ["get_gcp_transformer_from_file", "transform_layer_features"]

from .read_gcp_read import read_gcp_file

_logger = logging.getLogger(__name__)


def get_gcp_transformer_from_file(
    gcp_points_file_path: Path,
    method: QgsGcpTransformerInterface = QgsGcpTransformerInterface.TransformMethod.Helmert,
    *,
    filter_comments: bool = True,
) -> QgsGcpGeometryTransformer:
    """

    :param gcp_points_file_path:
    :type gcp_points_file_path:
    :param method:
    :type method:
    :param filter_comments:
    :type filter_comments:
    :return:
    :rtype:
    """
    source_xy, dest_xy = read_gcp_file(
        gcp_points_file_path, filter_comments=filter_comments
    )

    assert (len(source_xy) == len(dest_xy)) and len(
        source_xy
    ) >= QgsGcpTransformerInterface.create(
        QgsGcpTransformerInterface.TransformMethod(method)
    ).minimumGcpCount()

    return QgsGcpGeometryTransformer(
        method, (QgsPointXY(*s) for s in source_xy), (QgsPointXY(*d) for d in dest_xy)
    )


def transform_layer_features(
    layer: QgsVectorLayer,
    pre_transformer: Any | None,
    transformer: QgsGcpGeometryTransformer,
    tree_layer: QgsLayerTreeLayer,
) -> None:
    """

    :param layer:
    :type layer:
    :param pre_transformer:
    :type pre_transformer:
    :param transformer:
    :type transformer:
    :param tree_layer:
    :type tree_layer:
    :return:
    :rtype:
    """

    _logger.warning(f"Transforming geometry of layer with name: {layer.name()}")

    for idx, feat in enumerate(layer.getFeatures()):
        if not feat.hasGeometry():
            if False:
                assert (
                    feat.hasGeometry()
                ), f"Feature {idx} of {layer.name()} has no geometry"
            else:
                _logger.error(
                    f"Feature {idx} of {layer.name()} has no geometry, skipping"
                )
                continue
        geometry = feat.geometry()
        if pre_transformer:
            geometry.transform(
                pre_transformer, Qgis.TransformDirection.ForwardTransform
            )

        geom, ok = transformer.transform(geometry)

        if pre_transformer:
            geom.transform(pre_transformer, Qgis.TransformDirection.ReverseTransform)

        if not ok:
            _logger.error(
                f"Error while transforming {geom} in layer {tree_layer.layer().name()}"
            )
        feat.setGeometry(geom)
        layer.updateFeature(feat)
