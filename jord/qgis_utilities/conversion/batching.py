import logging
from typing import Any, Collection, Optional, Union

from qgis.analysis import QgsGcpGeometryTransformer
from qgis.core import (
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsLayerTreeNode,
)

from jord.qgis_utilities.conversion.gcp_transformer_factory import (
    transform_layer_features,
)
from jord.qgis_utilities.helpers import LayerEditingContext

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
    """

    :param selected_nodes:
    :type selected_nodes:
    :param transformer:
    :type transformer:
    :param pre_transformer:
    :type pre_transformer:
    :return:
    :rtype:
    """
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

    with LayerEditingContext("Layer geometry transformation", layer):

        transform_layer_features(layer, pre_transformer, transformer, tree_layer)

    layer.triggerRepaint()
