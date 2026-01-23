import geopandas
import momepy
import shapely
from typing import Optional, Union

__all__ = ["construct_centerline"]


def construct_centerline(
    input_geometry: shapely.Polygon,
    interpolation_distance: Optional[float] = None,
    truncate_endings: bool = True,
    merge_lines: bool = True,
    simplify_lines: bool = False,
) -> Union[shapely.LineString, shapely.MultiLineString]:
    if interpolation_distance is None:
        interpolation_distance = input_geometry.minimum_clearance

    if interpolation_distance < 1e-15:
        if isinstance(input_geometry, shapely.MultiPolygon):
            return shapely.MultiLineString([f.exterior for f in input_geometry.geoms])
        return input_geometry.exterior

    densified_border = input_geometry.segmentize(interpolation_distance * 0.9)

    voronoi_polys = shapely.voronoi_polygons(
        densified_border,
        only_edges=True,
    )  # equivalent to the scipy.spatial.Voronoi

    center_lines = geopandas.GeoDataFrame(
        geometry=geopandas.GeoSeries(voronoi_polys.geoms)
    ).sjoin(
        geopandas.GeoDataFrame(geometry=geopandas.GeoSeries(input_geometry)),
        predicate="within",
    )  # to select only the linestring within the input geometry

    if truncate_endings:
        graph = momepy.gdf_to_nx(center_lines)

        graph.remove_nodes_from(
            node for node, degree in dict(graph.degree()).items() if degree < 2
        )

        center_lines = momepy.nx_to_gdf(graph, points=False)

    ret = center_lines.unary_union

    if merge_lines:
        ret = shapely.line_merge(ret)

    if simplify_lines:
        ret = shapely.simplify(ret, tolerance=interpolation_distance * 0.1)

    if isinstance(ret, shapely.geometry.MultiLineString):
        geoms = list(ret.geoms)
        if len(geoms) == 1:
            return geoms[0]

    return ret
