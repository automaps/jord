from typing import Any, Generator

from qgis.core import QgsLayerTreeGroup, QgsLayerTreeLayer

__all__ = ["recurse_layers"]


def recurse_layers(group: QgsLayerTreeGroup) -> Generator[Any, None, None]:
    """

    :param group:
    :type group:
    """
    # QgsLayerTreeLayer
    for layer in group.children():
        if isinstance(layer, QgsLayerTreeGroup):
            yield from recurse_layers(layer)
        elif isinstance(layer, QgsLayerTreeLayer):
            yield layer
