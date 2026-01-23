__author__ = "heider"
__doc__ = r"""

           Created on 5/5/22
           """

from pathlib import Path

from typing import Any, Tuple, Union

__all__ = ["read_geometries"]


def read_geometries(
    fn: Union[str, Path], bbox: Tuple[float, float, float, float] = None
) -> Any:
    """
    reads to shapely geometries to features using fiona collection
    feature = dict('geometry': <shapely geometry>, 'properties': <dict with properties>

    :param fn:
    :param bbox:
    :return:
    """
    from fiona import collection
    from shapely.geometry import shape

    with collection(str(fn), "r") as c:
        ft_list = []
        c = c.items(bbox=bbox)
        for ft in c:
            if ft[1]["geometry"] is not None:
                ft_list.append(shape(ft[1]["geometry"]))

    return ft_list
