import logging
from shapely import Polygon

from .rings import ensure_ccw_ring, ensure_cw_ring

_logger = logging.getLogger(__name__)

__all__ = [
    "ensure_cw_poly",
    "ensure_ccw_poly",
]


def ensure_ccw_poly(polygon: Polygon) -> Polygon:
    """
    This function checks if the polygon is counter-clockwise if not it is reversed


    :param polygon: The polygon to check
    :return: Returns the polygon turned clockwise
    """

    return Polygon(
        shell=ensure_ccw_ring(polygon.exterior),
        holes=[ensure_ccw_ring(hole) for hole in polygon.interiors],
    )


def ensure_cw_poly(polygon: Polygon) -> Polygon:
    """
    This function checks if the polygon is clockwise if not it is reversed


    :param polygon: The polygon to check
    :return: Returns the polygon turned clockwise
    """

    return Polygon(
        shell=ensure_cw_ring(polygon.exterior),
        holes=[ensure_cw_ring(hole) for hole in polygon.interiors],
    )
