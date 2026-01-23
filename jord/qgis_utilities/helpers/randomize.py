import logging
import uuid

__all__ = ["randomize_field", "randomize_sub_tree_field"]

from typing import Collection, Union, Any

# noinspection PyUnresolvedReferences
from qgis.core import QgsLayerTreeGroup, QgsLayerTreeLayer, QgsLayerTreeNode

_logger = logging.getLogger(__name__)


def randomize_sub_tree_field(
    selected_nodes: Union[Any, Collection[Any]], field_name: str
) -> None:
    if isinstance(selected_nodes, QgsLayerTreeLayer):
        randomize_field(selected_nodes, field_name=field_name)
    elif isinstance(selected_nodes, QgsLayerTreeGroup):
        randomize_sub_tree_field(selected_nodes.children(), field_name=field_name)
    elif isinstance(selected_nodes, QgsLayerTreeNode):
        if selected_nodes.nodeType() == QgsLayerTreeNode.NodeGroup:
            randomize_sub_tree_field(selected_nodes.children(), field_name=field_name)
        else:
            _logger.error(
                f"Node {selected_nodes} was not supported in randomize_sub_tree_field, skipping"
            )
    else:
        if len(selected_nodes) == 0:
            _logger.error(
                f"'Number of selected nodes was {len(selected_nodes)}, please supply some"
            )
            return

        for group in iter(selected_nodes):
            if isinstance(group, QgsLayerTreeLayer):
                randomize_field(group, field_name=field_name)
            elif isinstance(group, QgsLayerTreeGroup):
                randomize_sub_tree_field(group.children(), field_name=field_name)
            elif isinstance(group, QgsLayerTreeNode):
                if group.nodeType() == QgsLayerTreeNode.NodeGroup:
                    randomize_sub_tree_field(group.children(), field_name=field_name)
                else:
                    _logger.error(
                        f"Node {group} was not supported in randomize_sub_tree_field, skipping"
                    )
            else:
                _logger.error(
                    f"Node {group} was not supported in randomize_sub_tree_field, skipping"
                )


def randomize_field(tree_layer: Any, field_name: str) -> None:  #: QgsLayerTreeLayer
    """
        https://qgis.org/pyqgis/3.28/core/QgsVectorLayer.html#qgis.core.QgsVectorLayer.changeAttributeValues

    changeAttributeValues
    fid: int, newValues: Dict[int, Any], oldValues: Dict[int, Any] = {}, skipDefaultValues: bool = False

        :param field_name:
        :param tree_layer:
        :return:
    """
    if tree_layer is None:
        _logger.error(f"Tree layer was None")
        return
    # logger.info(f'Randomizing {field_name} in {tree_layer.layer().name()}')

    layer = tree_layer.layer()

    field_idx = layer.fields().indexFromName(field_name)

    if field_idx >= 0:
        layer.startEditing()
        # layer.beginEditCommand(f"Regenerate {field_name}")
        _logger.info(
            f"Randomizing {field_name}:{field_idx} in {tree_layer.layer().name()}"
        )

        for i in range(layer.featureCount() + 1):
            layer.changeAttributeValue(i, field_idx, uuid.uuid4().hex)

        # layer.rollBack()
        # layer.endEditCommand()
        layer.commitChanges()
    else:
        _logger.error(f"Did not find {field_name} in {layer.name()}")
