from typing import Iterable, List, Tuple, Union

import numpy
import pyproj
import shapely.geometry
from shapely.ops import transform

__all__ = [
    "crs_transform_shapely",
    "get_helmert_transformation_parameters",
    "get_affine_transform_parameters",
]


def crs_transform_shapely(
    geoms: Union[
        shapely.geometry.base.BaseGeometry, Iterable[shapely.geometry.base.BaseGeometry]
    ],
    from_coordinate_system: str,
    to_coordinate_system: str,
) -> Union[
    shapely.geometry.base.BaseGeometry, List[shapely.geometry.base.BaseGeometry]
]:
    """
    Project space geometries from one coordinate system to another

    :param geoms: A list of SpacePolygons to project
    :param from_coordinate_system: The source coordinate system
    :param to_coordinate_system: The destination coordinate system
    :return: A list of SpacePolygons projected
    """

    source = pyproj.CRS(from_coordinate_system)
    destination = pyproj.CRS(to_coordinate_system)
    projection = pyproj.Transformer.from_crs(
        source, destination, always_xy=True
    ).transform
    #    project = pyproj.Transformer.from_proj(
    #    pyproj.Proj(init="epsg:4326"),  # source coordinate system
    #    pyproj.Proj(init="epsg:3857"),  # destination coordinate system
    # )

    if isinstance(geoms, Iterable):
        return [transform(projection, geometry) for geometry in geoms]

    return transform(projection, geoms)


def get_helmert_transformation_parameters(
    displacements: Iterable[Tuple[Tuple[float, float], Tuple[float, float]]],
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    # Calculate Helmert parameters for 2D transformation
    # https://homepage.univie.ac.at/Wolfgang.Kainz/Lehrveranstaltungen/15th_Nordic_Summer_School
    /The_Mathematics_of_GIS_Draft.pdf
    # https://riptutorial.com/numpy/example/16034/find-the-least-squares-solution-to-a-linear-system-with-np-linalg-lstsq

    # Displacement lines have to from local coordinate system to Webmercator.
    # The transformation is a 2d helmert and not affine, so the scale factor is the same in x and y direction
    # The angle between x and y axis have is also 90 degree.
    # This would not be the case if target project would have been WGS84

    :param displacements:
    :return:
    """
    A = []
    b = []
    for from_, to_ in displacements:
        from_x, from_y = from_
        to_x, to_y = to_

        A.append([from_x, from_y, 1, 0])
        b.append(to_x)
        A.append([from_y, -from_x, 0, 1])
        b.append(to_y)

    x, residuals, rank, s = numpy.linalg.lstsq(A, b, rcond=-1)

    return x, residuals


def get_affine_transform_parameters(
    displacements: Iterable[Tuple[Tuple[float, float], Tuple[float, float]]],
) -> List[float]:
    """

    :param displacements:
    :return:
    """
    transformation_params, _ = get_helmert_transformation_parameters(displacements)
    a, b, c, d = transformation_params
    return [a, b, -b, a, c, d]
