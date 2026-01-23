import logging
import shapely
from shapely import unary_union
from typing import Any, Callable, List, Mapping, Sequence, Union

from .geometry_types import is_multi
from .morphology import clean_shape, closing

__all__ = ["overlap_groups"]

_logger = logging.getLogger(__name__)


def overlap_groups(
    to_be_grouped: Union[
        Sequence[shapely.geometry.base.BaseGeometry],
        Mapping[Any, shapely.geometry.base.BaseGeometry],
    ],
    must_be_unique: bool = False,
    group_test: Callable = shapely.intersects,
) -> List[Mapping[Any, shapely.geometry.base.BaseGeometry]]:
    """

    Given a sequence of geometries `to_be_grouped`, this function will group
    the geometries based on a `group_test` function. `group_test` must return a bool indicating whether to
    group any two geometries

    `must_be_unique` allows us to assert whether all geometries will be possible grouped uniquely, e.g. if in
    `to_be_grouped` a multi shape could end up in 2 groups, we can disallow that.

    :param to_be_grouped:
    :param must_be_unique:
    :param group_test:
    :return:
    """

    if not isinstance(to_be_grouped, Mapping):
        to_be_grouped = dict(zip((i for i in range(len(to_be_grouped))), to_be_grouped))

    if must_be_unique:
        assert not any(is_multi(p) for p in to_be_grouped.values()), to_be_grouped

    unions = clean_shape(
        closing(unary_union(list(unary_union(v) for v in to_be_grouped.values())))
    )

    groups = []
    already_grouped = []

    if not is_multi(unions):
        groups.append(to_be_grouped)
    else:
        for union_part in unions.geoms:
            union_part = clean_shape(union_part)
            incidentee = {}
            for k, v in to_be_grouped.items():
                v = clean_shape(v)
                try:
                    g_test = group_test(v, union_part)
                except shapely.errors.GEOSException as e:
                    _logger.error(e)  # Assume overlap was found
                    g_test = True

                if g_test:
                    if must_be_unique:
                        assert k not in already_grouped, f"{k, already_grouped, v}"
                    incidentee[k] = v
                    already_grouped.append(k)
            groups.append(incidentee)

    return groups


if __name__ == "__main__":

    def demo():
        from shapely.geometry import box
        from pprint import pprint

        data = [
            box(1, 1, 3, 3),
            box(2, 2, 3, 3),
            box(4, 4, 6, 6),
            box(4, 4, 5, 5),
            box(5, 5, 6, 6),
            box(7, 7, 8, 8),
            box(1, 1, 2, 2),
            box(4, 4, 6, 6),
        ]

        pprint(overlap_groups(data))

        data = [
            box(1, 1, 3, 3),
            unary_union([box(2, 2, 3, 3), box(4, 4, 5, 5)]),
            box(4, 4, 6, 6),
            box(4, 4, 5, 5),
        ]

        pprint(overlap_groups(data))

        # pprint(overlap_groups(data, must_be_unique=True)) # FAILS!

    demo()
