from collections import defaultdict

import shapely
from copy import copy
from shapely.constructive import simplify
from shapely.geometry.base import GeometrySequence
from tqdm import tqdm
from typing import Collection, Dict, List, Sequence, Union

from jord.geometric_analysis import construct_centerline
from jord.shapely_utilities import (
    clean_shape,
    dilate,
    extend_line,
    is_multi,
    iter_polygons,
    opening,
    pro_closing,
)
from jord.shapely_utilities.desliver_wkt import a_wkt
from jord.shapely_utilities.lines import (
    ExtensionDirectionEnum,
    find_isolated_endpoints,
    linemerge,
    snap_endings_to_points,
)
from jord.shapely_utilities.morphology import closing, erode, pro_opening
from jord.shapely_utilities.subdivision import subdivide

__all__ = [
    "desliver",
    "cut_polygon",
    "multi_line_extend",
    "desliver_center_divide",
    "desliver_center_divide_shared",
    "desliver_least_intersectors_first",
]

from jord.shapely_utilities.projection import (
    get_min_max_projected_line,
    project_point_to_object,
)


def desliver(
    polygons: Collection[shapely.Polygon], buffer_size: float = 0.2
) -> List[shapely.geometry.Polygon]:
    buffered_exterior = []

    if isinstance(polygons, Sequence):
        polygons = list(polygons)

    for polygon in polygons:
        polygon: shapely.Polygon
        buffered_exterior.append(dilate(polygon, distance=buffer_size) - polygon)

    return buffered_exterior


def cut_polygon(
    polygon: shapely.Polygon, line_split_collection: List[shapely.LineString]
) -> GeometrySequence:
    line_split_collection.append(
        polygon.boundary
    )  # collection of individual linestrings for splitting in a list and add the polygon lines to it.
    merged_lines = linemerge(line_split_collection)
    border_lines = shapely.ops.unary_union(merged_lines)
    return shapely.ops.polygonize(border_lines)


def multi_line_extend(
    multi_line_string: Union[shapely.LineString, shapely.MultiLineString],
    distance: float,
) -> shapely.MultiLineString:
    isolated_endpoints = find_isolated_endpoints(multi_line_string)

    lines = []

    if isinstance(multi_line_string, shapely.LineString):
        ls = [multi_line_string]
    else:
        ls = multi_line_string.geoms

    for line in ls:
        start_point, end_point = shapely.Point(line.coords[0]), shapely.Point(
            line.coords[-1]
        )

        endpoint_in_isolated_points = end_point in isolated_endpoints

        direction = None
        if start_point in isolated_endpoints:
            if endpoint_in_isolated_points:
                direction = ExtensionDirectionEnum.both
            else:
                direction = ExtensionDirectionEnum.start
        elif endpoint_in_isolated_points:
            direction = ExtensionDirectionEnum.end

        if direction is not None:
            line = extend_line(line, offset=distance, simplify=False, side=direction)

        lines.append(line)

    return shapely.MultiLineString(lines)


def desliver_center_divide(
    polygons: Collection[shapely.Polygon],
    buffer_size: float = 0.2,
    post_process: bool = True,
    min_max_projection: bool = True,
    simplify_center_line: bool = False,
    close_res: bool = False,
) -> List[shapely.geometry.Polygon]:
    buffered_exterior = []

    if not isinstance(polygons, Sequence):
        polygons = list(polygons)

    for polygon in polygons:
        polygon: shapely.Polygon
        buffered_exterior.append(dilate(polygon, distance=buffer_size) - polygon)

    augmented_polygons = []

    intersections = []
    for ith in range(len(buffered_exterior)):
        a = buffered_exterior.copy()
        b = a.pop(ith)
        intersections.append(shapely.unary_union(a) & b)

    for ith, intersection in tqdm(enumerate(intersections)):
        minimum_clearance = intersection.minimum_clearance

        intersection = shapely.unary_union(list(iter_polygons(intersection)))

        center_line = construct_centerline(
            intersection, interpolation_distance=minimum_clearance / 3.14
        )

        if simplify_center_line:
            center_line = simplify_center_line(
                center_line, preserve_topology=False, tolerance=minimum_clearance / 2.0
            )

            center_line = simplify_center_line(
                center_line, preserve_topology=True, tolerance=minimum_clearance * 2.0
            )

        # TODO FIT LINE TO JAGGED LINE

        center_line = multi_line_extend(center_line, distance=minimum_clearance)

        if isinstance(intersection, shapely.Polygon):
            snapping_points = [
                shapely.Point(c) for c in subdivide(intersection).exterior.coords
            ]
        else:
            snapping_points = [
                shapely.Point(c)
                for inter in intersection.geoms
                for c in subdivide(inter).exterior.coords
            ]

        snapped_center_line = snap_endings_to_points(
            center_line, snapping_points=snapping_points, max_distance=minimum_clearance
        )

        poly = polygons[ith]

        if min_max_projection:
            for line in snapped_center_line.copy():
                projected_line = get_min_max_projected_line(line, poly)

                start, end = shapely.Point(projected_line.coords[0]), shapely.Point(
                    projected_line.coords[-1]
                )

                start_line, end_line = (
                    extend_line(
                        shapely.LineString(
                            (start, project_point_to_object(start, poly))
                        ),
                        offset=minimum_clearance,
                    ),
                    extend_line(
                        shapely.LineString((end, project_point_to_object(end, poly))),
                        offset=minimum_clearance,
                    ),
                )

                snapped_center_line.extend((start_line, end_line))

        res = cut_polygon(intersection, snapped_center_line)

        augmented = copy(poly)
        for r in res:
            un = r | poly
            re = erode(dilate(un, distance=1e-10), distance=1e-9)
            if is_multi(re):
                continue

            f = closing(un)

            if True:
                augmented |= f
            else:
                k = r & poly
                if k:
                    if isinstance(k, shapely.LineString):
                        if k.length >= minimum_clearance:
                            augmented |= r

        augmented = pro_opening(augmented, distance=minimum_clearance / 2.0)
        augmented_polygons.append(augmented)

    if post_process:
        if True:
            post_processed = []
            for ith in range(len(augmented_polygons)):
                a = augmented_polygons.copy()
                b = a.pop(ith)
                post_processed.append(
                    opening(
                        b - shapely.unary_union(a), distance=minimum_clearance / 2.0
                    ).simplify(
                        tolerance=minimum_clearance / 2.0, preserve_topology=False
                    )
                )
        else:
            post_processed = augmented_polygons

        if True:
            post_processed = shapely.MultiPolygon(post_processed).simplify(
                tolerance=minimum_clearance / 2.0, preserve_topology=True
            )

            post_processed_list = list(post_processed.geoms)
        else:
            post_processed_list = post_processed

        post_snaps = 2
        for _ in range(post_snaps):
            for ith in range(len(post_processed_list)):
                a = post_processed_list.copy()

                p = a.pop(ith)

                if True:  # Union
                    s = shapely.unary_union([clean_shape(l) for l in a])
                elif False:  # Deconstruct
                    if isinstance(s, shapely.geometry.Polygon):
                        coords = s.exterior.coords
                    else:
                        coords = []
                        for g in s.geoms:
                            coords.extend(g.exterior.coords)

                    s = [shapely.Point(c) for c in coords]
                else:
                    s = a

                if close_res:
                    ll = polygons.copy()
                    lp = ll.pop(ith)

                    post_processed_list[ith] = (
                        pro_closing(
                            shapely.snap(p, s, tolerance=minimum_clearance),
                            distance=minimum_clearance * 2.0,
                        )
                        | lp
                    ) - shapely.unary_union(ll)
                else:
                    post_processed_list[ith] = opening(
                        shapely.snap(p, s, tolerance=minimum_clearance),
                        distance=minimum_clearance * 2.0,
                    )

        return post_processed_list

    return augmented_polygons


def desliver_center_divide_shared(
    polygons: Collection[shapely.Polygon],
    buffer_size: float = 0.2,
    post_process: bool = True,
    min_max_projection: bool = False,
) -> List[shapely.geometry.Polygon]:
    buffered_exterior = []

    if isinstance(polygons, Sequence):
        polygons = list(polygons)

    for polygon in polygons:
        polygon: shapely.Polygon
        buffered_exterior.append(dilate(polygon, distance=buffer_size) - polygon)

    augmented_polygons = []

    intersections = []
    for ith in range(len(buffered_exterior)):
        a = buffered_exterior.copy()
        b = a.pop(ith)
        intersections.append(shapely.unary_union(a) & b)

    for ith, intersection in tqdm(enumerate(intersections)):
        minimum_clearance = intersection.minimum_clearance

        center_line = construct_centerline(
            intersection, interpolation_distance=minimum_clearance / 2.0
        )

        center_line = simplify(
            center_line, preserve_topology=False, tolerance=minimum_clearance / 2.0
        )

        center_line = simplify(
            center_line, preserve_topology=True, tolerance=minimum_clearance * 2.0
        )

        center_line = multi_line_extend(center_line, distance=minimum_clearance)

        if isinstance(intersection, shapely.Polygon):
            snapping_points = [
                shapely.Point(c) for c in subdivide(intersection).exterior.coords
            ]
        else:
            snapping_points = [
                shapely.Point(c)
                for inter in intersection.geoms
                for c in subdivide(inter).exterior.coords
            ]

        snapped_center_line = snap_endings_to_points(
            center_line, snapping_points=snapping_points, max_distance=minimum_clearance
        )

        poly = polygons[ith]

        if min_max_projection:
            for line in snapped_center_line.copy():
                projected_line = get_min_max_projected_line(line, poly)

                start, end = shapely.Point(projected_line.coords[0]), shapely.Point(
                    projected_line.coords[-1]
                )

                start_line, end_line = (
                    extend_line(
                        shapely.LineString(
                            (start, project_point_to_object(start, poly))
                        ),
                        offset=minimum_clearance,
                    ),
                    extend_line(
                        shapely.LineString((end, project_point_to_object(end, poly))),
                        offset=minimum_clearance,
                    ),
                )

                snapped_center_line.extend((start_line, end_line))

        res = cut_polygon(intersection, snapped_center_line)

        augmented = copy(poly)
        for r in res:
            un = r | poly
            re = erode(dilate(un, distance=1e-10), distance=1e-9)
            if is_multi(re):
                continue

            f = closing(un)

            if True:
                augmented |= f
            else:
                k = r & poly
                if k:
                    if isinstance(k, shapely.LineString):
                        if k.length >= minimum_clearance:
                            augmented |= r

        augmented = pro_opening(augmented, distance=minimum_clearance / 2.0)
        augmented_polygons.append(augmented)

    if post_process:
        post_processed = []

        for ith in range(len(augmented_polygons)):
            a = augmented_polygons.copy()
            b = a.pop(ith)
            post_processed.append(
                opening(b - shapely.unary_union(a), distance=minimum_clearance / 2.0)
            )

        # for p in post_processed:
        #  ...

        post_processed = list(
            shapely.MultiPolygon(post_processed)
            .simplify(tolerance=minimum_clearance / 2.0)
            .geoms
        )

        return post_processed

    return augmented_polygons


def desliver_least_intersectors_first(
    polygons: Collection[shapely.Polygon], buffer_size: float = 0.2
) -> Dict[int, shapely.geometry.Polygon]:
    buffered_exterior = []

    if isinstance(polygons, Sequence):
        polygons = list(polygons)

    for polygon in polygons:
        polygon: shapely.Polygon
        buffered_exterior.append(dilate(polygon, distance=buffer_size) - polygon)

    intersections = []
    for ith in range(len(buffered_exterior)):
        a = buffered_exterior.copy()
        b = a.pop(ith)
        intersections.append(shapely.unary_union(a) & b)

    inter_intersections = defaultdict(dict)
    num_intersections = len(intersections)
    for ith in range(num_intersections):
        for jth in range(num_intersections):
            if ith == jth:
                continue

            if (
                False
            ):  # TODO: OPTIMISATION when picking least intersectors to get intersection?
                if ith in inter_intersections[jth]:
                    continue

            c = intersections[ith] & intersections[jth]

            if not c.is_empty:
                inter_intersections[ith][jth] = c

    already_assigned = defaultdict(list)
    out = {}
    for ith_poly, intersectors in sorted(
        inter_intersections.items(), key=lambda d: len(d[-1].values()), reverse=False
    ):
        p = polygons[ith_poly]

        if intersectors:
            for ith_intersector, intersection in intersectors.items():
                already_assigned[ith_poly].append(ith_intersector)

                if ith_poly in already_assigned[ith_intersector]:
                    continue

                p |= intersection - polygons[ith_intersector]

            out[ith_poly] = pro_opening(p, distance=buffer_size)
        else:
            out[ith_poly] = p

    assert len(out) == len(polygons)

    return out


if __name__ == "__main__":

    def sauihd2():
        polygons = list(shapely.from_wkt(a_wkt).geoms)
        once = desliver_least_intersectors_first(polygons)
        out = desliver_least_intersectors_first(list(once.values()))

        c = shapely.MultiPolygon(iter_polygons(out.values()))
        ...

    def sauihd():
        polygons = list(shapely.from_wkt(a_wkt).geoms)
        once = desliver(polygons)
        out = desliver(list(once.values()))

        c = shapely.MultiPolygon(iter_polygons(out.values()))
        ...

    def sauihd3():
        polygons = list(shapely.from_wkt(a_wkt).geoms)
        once = desliver_center_divide(polygons)
        out = desliver_center_divide(list(once.values()))

        c = shapely.MultiPolygon(iter_polygons(out.values()))
        print(c.wkt)
        ...

    sauihd3()
