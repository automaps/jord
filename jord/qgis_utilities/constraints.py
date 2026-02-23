from typing import Iterable

from qgis.core import (
    QgsVectorLayer,
)

__all__ = ["set_geometry_constraints"]


def set_geometry_constraints(layers: QgsVectorLayer) -> None:
    """

    :param layers:
    :type layers:
    :return:
    :rtype:
    """
    if layers is None:
        return

    geometry_options = [
        "QgsIsValidCheck",
    ]

    gap_check_configuration = {
        "allowedGapsBuffer": 0,
        "allowedGapsEnabled": False,
        "allowedGapsLayer": "",
    }

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layer in layers_inner:
                    if layer:
                        layer.geometryOptions().setGeometryChecks(geometry_options)
                        # layer.geometryOptions().setCheckConfiguration("QgsGeometryGapCheck", gap_check_configuration)
                        # layer.geometryOptions().setGeometryPrecision(0.0001)
                        layer.geometryOptions().setRemoveDuplicateNodes(True)
            else:
                layers_inner.geometryOptions().setGeometryChecks(geometry_options)
                layers_inner.geometryOptions().setRemoveDuplicateNodes(True)
