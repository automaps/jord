from typing import Any, Collection

__all__ = [
    "sanitise_wkb",
    "sanitise_wkt",
    "explode_geometry_collection",
    "wkb_geom_constructor",
]


def sanitise_wkb() -> str:
    """ """
    ...


def sanitise_wkt() -> str:
    """ """
    ...


def explode_geometry_collection() -> Collection[str]:
    """ """
    ...


def wkb_geom_constructor(wkb: bytes) -> Any:
    """

    :param wkb:
    :type wkb:
    :return:
    :rtype:
    """
    from qgis.core import QgsGeometry

    geom = QgsGeometry()
    geom.fromWkb(wkb)
    return geom
