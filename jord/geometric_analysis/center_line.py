import numpy
import shapely.geometry
from numpy import array
from scipy.spatial import Voronoi
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
from shapely.ops import unary_union
from typing import Iterable, List, Tuple, Union
from warg import Number

from jord.shapely_utilities.polygons import iter_polygons, polygon_has_interior_rings

__all__ = ["find_centerline"]


def find_centerline(
    input_geometry: Union[Polygon, MultiPolygon], step_size: Number = 0.5
) -> MultiLineString:
    """


    :param input_geometry: input geometry
    :type input_geometry: Union[Polygon, MultiPolygon]
    :param step_size: densify the input geometry border by placing additional points at this distance, in meters
    :type step_size: Optional[float]
    :raises NotImplementedError: input geometry is not of type Union[Polygon, MultiPolygon]
    """

    if not (
        isinstance(input_geometry, Polygon) or isinstance(input_geometry, MultiPolygon)
    ):
        raise NotImplementedError

    step_size = abs(step_size)

    ext_xy = input_geometry.envelope.exterior.xy
    _min_x, _min_y = (
        int(min(ext_xy[0])),
        int(min(ext_xy[1])),
    )

    vertices, ridges = get_voronoi_vertices_and_ridges(
        input_geometry, step_size, minx=_min_x, miny=_min_y
    )

    lines = []
    for ridge in ridges:
        if ridge_is_finite(ridge):
            starting_point = create_point_with_restored_coordinates(
                x=vertices[ridge[0]][0],
                y=vertices[ridge[0]][1],
                _min_x=_min_x,
                _min_y=_min_y,
            )
            ending_point = create_point_with_restored_coordinates(
                x=vertices[ridge[1]][0],
                y=vertices[ridge[1]][1],
                _min_x=_min_x,
                _min_y=_min_y,
            )
            linestring = LineString((starting_point, ending_point))

            if linestring_is_within_input_geometry(linestring, input_geometry):
                lines.append(linestring)

    if len(lines) < 2:
        raise Exception("too few ridges")

    return MultiLineString(lines=unary_union(lines))


def get_voronoi_vertices_and_ridges(
    _input_geometry: shapely.geometry.base.BaseGeometry,
    _step_size: float,
    minx: float,
    miny: float,
) -> Tuple[numpy.ndarray, List[List[int]]]:
    borders = densify_border(_input_geometry, _step_size, minx, miny)

    voronoi_diagram = Voronoi(borders)
    return voronoi_diagram.vertices, voronoi_diagram.ridge_vertices


def ridge_is_finite(ridge: Iterable) -> bool:
    return -1 not in ridge


def create_point_with_restored_coordinates(
    x: float, y: float, _min_x: float, _min_y: float
) -> Tuple[float, float]:
    return x + _min_x, y + _min_y


def linestring_is_within_input_geometry(
    linestring: LineString, input_geometry: shapely.geometry.base.BaseGeometry
) -> bool:
    return linestring.within(input_geometry) and len(linestring.coords[0]) > 1


def densify_border(
    _input_geometry: shapely.geometry.base.BaseGeometry,
    _step_size,
    minx: float,
    miny: float,
) -> numpy.ndarray:
    polygons = iter_polygons(_input_geometry)
    points = []
    for polygon in polygons:
        points += interpolated_boundary(polygon.exterior, _step_size, minx, miny)
        if polygon_has_interior_rings(polygon):
            for interior in polygon.interiors:
                points += interpolated_boundary(
                    interior, _step_size, minx=minx, miny=miny
                )

    return array(points)


def interpolated_boundary(
    boundary: shapely.geometry.base.BaseGeometry,
    _step_size: float,
    minx: float,
    miny: float,
) -> List[Tuple[float, float]]:
    line = LineString(boundary)

    return (
        [get_coordinates_of_first_point(line, minx, miny)]
        + get_coordinates_of_interpolated_points(
            line, _step_size, min_x=minx, min_y=miny
        )
        + [get_coordinates_of_last_point(line, minx=minx, miny=miny)]
    )


def create_point_with_reduced_coordinates(
    x: float, y: float, _min_x: float, _min_y: float
) -> Tuple[float, float]:
    return x - _min_x, y - _min_y


def get_coordinates_of_first_point(
    linestring: LineString, minx: float, miny: float
) -> Tuple[float, float]:
    return create_point_with_reduced_coordinates(
        x=linestring.xy[0][0], y=linestring.xy[1][0], _min_x=minx, _min_y=miny
    )


def get_coordinates_of_last_point(
    linestring: LineString, minx: float, miny: float
) -> Tuple[float, float]:
    return create_point_with_reduced_coordinates(
        x=linestring.xy[0][-1], y=linestring.xy[1][-1], _min_x=minx, _min_y=miny
    )


def get_coordinates_of_interpolated_points(
    linestring: LineString, _step_size: Number, min_x: float, min_y: float
) -> List[Tuple[float, float]]:
    interpolation_distance = _step_size
    intermediate_points = []
    while interpolation_distance < linestring.length:
        point = linestring.interpolate(interpolation_distance)
        reduced_point = create_point_with_reduced_coordinates(
            x=point.x, y=point.y, _min_x=min_x, _min_y=min_y
        )
        intermediate_points.append(reduced_point)
        interpolation_distance += _step_size

    return intermediate_points


if __name__ == "__main__":

    def uashdua():
        from shapely.geometry import Polygon
        from jord.qlive_utilities import AutoQliveClient

        polygon = Polygon([[0, 0], [0, 4], [4, 4], [4, 0]])

        with AutoQliveClient() as qlive:
            qlive.add_shapely_geometry(polygon)
            qlive.add_shapely_geometry(find_centerline(polygon))

    uashdua()
