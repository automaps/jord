# !/usr/bin/python

import logging

# noinspection PyUnresolvedReferences
from qgis.analysis import QgsGcpGeometryTransformer, QgsGcpTransformerInterface

# noinspection PyUnresolvedReferences
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsLayerTreeNode,
    QgsProject,
)
from typing import Any, Collection, Optional, Union

_logger = logging.getLogger(__name__)

__all__ = ["transform_features", "transform_sub_tree_features"]


def transform_sub_tree_features(
    selected_nodes: Union[
        Any,
        Collection[Any],
        # QgsLayerTreeGroup,
        # QgsLayerTreeLayer,
        # QgsLayerTreeNode
    ],
    transformer: QgsGcpGeometryTransformer,
    pre_transformer: Optional[Any] = None,
) -> None:
    if isinstance(selected_nodes, QgsLayerTreeLayer):
        transform_features(
            selected_nodes, transformer=transformer, pre_transformer=pre_transformer
        )
    elif isinstance(selected_nodes, QgsLayerTreeGroup):
        transform_sub_tree_features(
            selected_nodes.children(),
            transformer=transformer,
            pre_transformer=pre_transformer,
        )
    elif isinstance(selected_nodes, QgsLayerTreeNode):
        if selected_nodes.nodeType() == QgsLayerTreeNode.NodeGroup:
            transform_sub_tree_features(
                selected_nodes.children(),
                transformer=transformer,
                pre_transformer=pre_transformer,
            )
        else:
            _logger.error(
                f"Node {selected_nodes} was not supported in transform_sub_tree_features, skipping"
            )
    else:
        if len(selected_nodes) == 0:
            _logger.error(
                f"'Number of selected nodes was {len(selected_nodes)}, please supply some"
            )
            return

        for group in iter(selected_nodes):
            if isinstance(group, QgsLayerTreeLayer):
                transform_features(
                    group, transformer=transformer, pre_transformer=pre_transformer
                )
            elif isinstance(group, QgsLayerTreeGroup):
                transform_sub_tree_features(
                    group.children(),
                    transformer=transformer,
                    pre_transformer=pre_transformer,
                )
            elif isinstance(group, QgsLayerTreeNode):
                if group.nodeType() == QgsLayerTreeNode.NodeGroup:
                    transform_sub_tree_features(
                        group.children(),
                        transformer=transformer,
                        pre_transformer=pre_transformer,
                    )
                else:
                    _logger.error(
                        f"Node {group} was not supported in transform_sub_tree_features, skipping"
                    )
            else:
                _logger.error(
                    f"Node {group} was not supported in transform_sub_tree_features, skipping"
                )


def transform_features(
    tree_layer: Any,
    transformer: QgsGcpGeometryTransformer,
    pre_transformer: Optional[Any] = None,
) -> None:  #: QgsLayerTreeLayer
    """

    :param pre_transformer:
    :param transformer:
    :param tree_layer:
    :return:
    """

    if tree_layer is None:
        _logger.error(f"Tree layer was None")
        return

    layer = tree_layer.layer()

    if not layer.isValid():
        _logger.error(f"{layer.name()} is not valid!")
        return

    layer.startEditing()

    _logger.warning(
        f"Transforming geometry of layer with name: {tree_layer.layer().name()}"
    )

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

    layer.endEditCommand()
    layer.commitChanges()
    layer.triggerRepaint()
