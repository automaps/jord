from typing import Sequence

from shapely.geometry import LineString, Polygon


def is_2d_translatable():
    """ """
    ...


def has_touches_across_centroid_buffer(
    poly: Polygon,
    exterior_intersections: Sequence[LineString],
    centroid_buffer_size: float = 0.1,
) -> bool:
    """

    :param poly:
    :type poly:
    :param exterior_intersections:
    :type exterior_intersections:
    :param centroid_buffer_size:
    :type centroid_buffer_size:
    """
    poly.centroid.buffer()

    ...


def is_simple_shape():
    """ """
    ...


def has_3_sides_touching():
    """ """
    ...
