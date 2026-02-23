from typing import Optional, Sequence, Tuple, Union

from shapely import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

from jord.shapely_utilities import (
    closest_object,
    explode_polygons,
    extend_line,
    remove_redundant_nodes,
    shift_point,
    split_line,
)

__all__ = [
    "snap_lines",
    "split_lines",
    "intersection_points",
    "clip_lines_with_polygon",
]

EPSILON = 1e-6


def snap_lines(
    lines: Sequence[LineString],
    max_dist: float,
    tolerance: float = 1e-3,
    return_index: bool = False,
) -> Union[Sequence[LineString], Tuple[Sequence[LineString], Sequence[int]]]:
    """
    Snap lines together if the endpoint of one line1 is at most max_dist apart from the line2.
    Both lines are snapped by extending line1 towards line2
    the max distance is measured in the direction of the line1

    :param lines: a list of LineStrings or a MultiLineString
    :param max_dist: maximum distance two endpoints may be joined together
    :param tolerance:
    :param return_index:
    :return:
    """
    import rtree

    # extend all lines with max_dist to snap lines at a sharp angle
    lines_ext = [extend_line(line, max_dist) for line in lines]

    # build spatial index of line bounding boxes
    tree_idx = rtree.index.Index()
    lines_bbox = [l.bounds for l in lines_ext]
    for i, bbox in enumerate(lines_bbox):
        tree_idx.insert(i, bbox)

    lines_snap = []
    idx_snapped = []
    for i1, line in enumerate(lines):
        if isinstance(line, LineString):
            for side in ["start", "end"]:
                coords = line.coords[:]
                # make line extensions
                if side == "start":
                    ext = LineString(
                        [shift_point(coords[0], coords[1], -1.0 * max_dist), coords[0]]
                    )
                    pnt_from = Point(coords[0])
                elif side == "end":
                    ext = LineString(
                        [
                            coords[-1],
                            shift_point(coords[-1], coords[-2], -1.0 * max_dist),
                        ]
                    )
                    pnt_from = Point(coords[-1])

                # point instead of line if max_dist is zero (only clipping)
                if max_dist == 0:
                    ext = pnt_from

                # find close-by lines based on bounds with spatial index
                if tolerance > 0:
                    hits = list(tree_idx.intersection(ext.buffer(tolerance).bounds))
                else:
                    hits = list(tree_idx.intersection(ext.bounds))
                lines_hit = MultiLineString([lines_ext[i] for i in hits if i != i1])
                # find intersection points. function yields list of points
                int_points = intersection_points([ext], lines_hit, tolerance=tolerance)
                if len(int_points) == 0:
                    continue

                # if intersection yields something else then a Point, break down to nearest point
                if len(int_points) > 1:
                    # if more intersections, find closest
                    pnt_to = closest_object(int_points, pnt_from)[0]
                else:
                    pnt_to = int_points[0]

                # at this point pnt_to is the closest intersecting point
                if pnt_from != pnt_to:  # check if lines are not already touching
                    # snap line towards pnt_to
                    if side == "start":
                        coords[0] = pnt_to.coords[0]
                    elif side == "end":
                        coords[-1] = pnt_to.coords[0]
                    line = LineString(coords)
                    if i1 not in idx_snapped:
                        # bookkeeping: list with changes features
                        idx_snapped.append(i1)

            lines_snap.append(line)

    if return_index:
        return lines_snap, idx_snapped

    return lines_snap


def split_lines(
    lines: Sequence[LineString],
    points: Optional[Sequence[Point]] = None,
    tolerance: float = 0.0,
    return_index: bool = False,
) -> Union[Sequence[LineString], Tuple[Sequence[LineString], Sequence[int]]]:
    """
    split lines at intersection, or if given, at points

    :param lines:
    :param points:
    :param tolerance:
    :param return_index:
    :return:
    """
    import rtree

    if isinstance(points, Point):
        points = [points]

    # create output list
    lines_out = []
    index_out = []

    # build spatial index
    if points is None:
        # build spatial index of line bounding boxes
        tree_idx = rtree.index.Index()
        lines_bbox = [l.bounds for l in lines]
        for i, bbox in enumerate(lines_bbox):
            tree_idx.insert(i, bbox)
    else:
        # build spatial index of points
        tree_idx = rtree.index.Index()
        for i, p in enumerate(points):
            tree_idx.insert(i, p.buffer(tolerance).bounds)

    # loop through lines and split lines with split point
    for idx, line in enumerate(lines):
        if points is None:
            # find close-by lines based on bounds with spatial index
            hits = list(tree_idx.intersection(lines_bbox[idx]))
            lines_hit = MultiLineString([lines[i] for i in hits if i != idx])
            # find line intersections
            # lines_other = [l for i, l in enumerate(lines) if i != idx]
            split_points = intersection_points([line], lines_hit, tolerance=tolerance)
        else:
            # find close-by points based on bounds of line with spatial index
            hits = list(tree_idx.intersection(line.bounds))
            points_hit = [points[i] for i in hits]
            # find points which intersects with line
            split_points = [p for p in points_hit if line.distance(p) <= tolerance]
            # split_points = [p for p in points if line.distance(p) <= tolerance]

        # check if intersections for line
        if len(split_points) >= 1:
            for p in split_points:
                line = split_line(line, p, tolerance=tolerance)
            for l in line:
                lines_out.append(l)
                index_out.append(idx)
        else:
            lines_out.append(line)
            index_out.append(idx)

    if return_index:
        return remove_redundant_nodes(lines_out), index_out

    return remove_redundant_nodes(lines_out)


def clip_lines_with_polygon(
    lines: Sequence[LineString],
    polygon: Polygon,
    tolerance: float = 1e-3,
    within: bool = True,
    return_index: bool = False,
) -> Union[Sequence[LineString], Tuple[Sequence[LineString], Sequence[int]]]:
    """clip lines based on polygon outline"""
    # get boundaries of polygon
    boundaries = explode_polygons(polygon)
    # find intersection points of boundaries and lines and split lines based on it
    int_points = intersection_points(lines, boundaries)
    lines_split, index = split_lines(
        lines, int_points, tolerance=tolerance, return_index=True
    )

    # select lines that are contained by polygon
    polygon_buffer = polygon.buffer(
        tolerance
    )  # small buffer to allow for use 'within' function
    if within:
        lines_clip = [line for line in lines_split if line.within(polygon_buffer)]
        index = [
            i for i, line in zip(index, lines_split) if line.within(polygon_buffer)
        ]
    else:
        lines_clip = [line for line in lines_split if not line.within(polygon_buffer)]
        index = [
            i for i, line in zip(index, lines_split) if not line.within(polygon_buffer)
        ]
    if return_index:
        return lines_clip, index

    return lines_clip


def intersection_points(
    lines1, lines2=None, tolerance: float = 0.0, min_spacing: float = 0
):
    """creates list with points of line intersections. if intersection is other type than a point,
    it is broken down to points of its coordinates

    :param tolerance:
    :param min_spacing:
    :param lines1: MultiLineString or list of lines
    :param lines2: MultiLineString or list of lines, if None find intersections amongst lines1
    :return: list with shapely points of intersection
    """
    import rtree

    points = []
    tree_idx_pnt = rtree.index.Index()
    ipnt = 0

    if lines2 is None:
        # build spatial index for lines1
        tree_idx = rtree.index.Index()
        lines_bbox = [l.bounds for l in lines1]
        for i, bbox in enumerate(lines_bbox):
            tree_idx.insert(i, bbox)

    # create multilinestring of close-by lines
    for i1, l1 in enumerate(lines1):
        if lines2 is None:
            # find close-by lines based on bounds with spatial index
            hits = list(tree_idx.intersection(lines_bbox[i1]))
            lines_hit = MultiLineString([lines1[i] for i in hits if i != i1])
        else:
            lines_hit = MultiLineString(lines2)

        if tolerance > 0:
            l1 = extend_line(l1, tolerance)

        x = l1.intersection(lines_hit)
        if not x.is_empty:
            if isinstance(x, Point):
                pnts = [x]

            else:
                if isinstance(x, MultiPoint):
                    pnts = [Point(geom) for geom in x]
                elif isinstance(x, (MultiLineString, MultiPolygon, GeometryCollection)):
                    pnts = [Point(coords) for geom in x for coords in geom.coords]
                elif isinstance(x, (LineString, Polygon)):
                    pnts = [Point(coords) for coords in x.coords]
                else:
                    raise NotImplementedError("intersection yields bad type")

            for pnt in pnts:
                if min_spacing > 0:
                    if ipnt > 0:
                        hits = list(tree_idx_pnt.intersection(pnt.bounds))
                    else:
                        hits = []

                    if len(hits) == 0:  # no pnts within spacing
                        ipnt += 1
                        tree_idx_pnt.insert(ipnt, pnt.buffer(min_spacing).bounds)
                        points.append(pnt)
                else:
                    points.append(pnt)

    return points
