import logging

# noinspection PyUnresolvedReferences
from qgis.core import QgsLayerTreeGroup, QgsLayerTreeLayer, QgsProject

# noinspection PyUnresolvedReferences
from qgis.utils import iface
from typing import Any, Optional, Union

__all__ = [
    "duplicate_groups",
    "select_layer_in_group",
    "is_group_selected",
    "duplicate_tree_node",
]

from jord.qgis_utilities.helpers.copying import deepcopy_layer

try:
    from types import EllipsisType
except ImportError:
    EllipsisType = type(...)

_logger = logging.getLogger(__name__)


def duplicate_groups(
    group_to_duplicate: Any,
    *,
    group_parent: Optional[Any] = None,
    new_name: Union[str, EllipsisType, None] = None,
) -> QgsLayerTreeGroup:
    if group_to_duplicate is None:
        _logger.error("Group was None")
        return

    _logger.info(f"Duplicating {group_to_duplicate.name()}")

    if new_name is ... or new_name == "" or new_name is None:
        new_name = f"{group_to_duplicate.name()} (Copy)"

    sub_items = []
    assert (
        group_to_duplicate is not None
    ), f"{group_to_duplicate=} is required to create a duplicate group"

    if group_parent is None:
        group_parent = group_to_duplicate.parent()

    if group_parent is None:
        raise ValueError(f"Group parent was not found for {group_to_duplicate}")

    new_group_parent = group_parent.addGroup(new_name)
    for original_group_child in group_to_duplicate.children():
        if isinstance(original_group_child, QgsLayerTreeGroup):
            new_sub_group, sub_sub_items = duplicate_groups(
                original_group_child, group_parent=new_group_parent, new_name=...
            )
            sub_items.extend([new_sub_group, *sub_sub_items])
        elif isinstance(original_group_child, QgsLayerTreeLayer):
            sub_items.append(
                duplicate_tree_node(new_group_parent, original_group_child)
            )
        else:
            _logger.error(f"{original_group_child} no supported in duplication")

    return new_group_parent, sub_items


def duplicate_tree_node(
    new_group_parent: Any, original_group_child: Any, new_name: Optional[str] = None
) -> Any:
    original_layer = original_group_child.layer()
    new_layer_copy = deepcopy_layer(original_layer)

    if new_name is not None:
        new_layer_copy.setName(new_name)

    QgsProject.instance().addMapLayer(new_layer_copy, False)

    if False:
        new_layer_tree_node = QgsLayerTreeLayer(
            new_layer_copy
        )  # WORKS BUT MISSING STYLING
        new_group_parent.addChildNode(new_layer_tree_node)
    elif False:
        # Does not WORK EITHER
        new_layer_tree_node = QgsLayerTreeLayer(
            new_layer_copy.id(),
            original_layer.name(),
            new_layer_copy.source(),
            original_layer.providerType(),
        )
    elif False:
        # THIS DOES NOT WORK!!!
        new_layer_tree_node = (
            original_group_child.clone()
        )  # THIS JUST CREATES NEW VIEW of the same data!!!!
        new_layer_tree_node.layer().setDataSource(
            new_layer_copy.source(),
            new_layer_copy.name(),
            new_layer_copy.providerType(),
        )
    elif True:
        new_layer_node = new_group_parent.insertLayer(0, new_layer_copy)
        new_layer_node.setItemVisibilityChecked(original_group_child.isVisible())
    else:
        raise Exception()

    return new_layer_copy


def select_layer_in_group(layer_name: Any, group_name: Any) -> None:
    group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
    if group is not None:
        for child in group.children():
            if child.name() == layer_name:
                iface.setActiveLayer(child.layer())


def is_group_selected(group_name: Any) -> Any:
    group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
    return group in iface.layerTreeView().selectedNodes()
