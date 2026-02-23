from typing import List, Optional, Tuple

import shapely

__all__ = ["split_enveloping_geometry"]


def split_enveloping_geometry(
    geoms: List[shapely.geometry.base.BaseGeometry],
) -> Optional[
    Tuple[shapely.geometry.base.BaseGeometry, List[shapely.geometry.base.BaseGeometry]]
]:
    """
    Splits the enveloping geometry from the rest, if any, otherwise None.

    :param geoms:
    :return:
    """
    for geom in geoms:
        rest = set(geoms) - {geom}
        if all([shapely.contains(geom, r) for r in rest]):
            return geom, [*rest]
