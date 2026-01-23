import shapely
from shapely.geometry.linestring import LineString
from shapely.geometry.polygon import LinearRing, Polygon
from typing import Union
from warg import pairs

from jord.shapely_utilities.lines import linemerge

__all__ = ["subdivide", "subdivide_polygon", "subdivide_line", "subdivide_ring"]


def subdivide(
    geom: Union[LineString, LinearRing, Polygon],
) -> Union[LineString, LinearRing, Polygon]:
    if isinstance(geom, LineString):
        return subdivide_line(geom)
    elif isinstance(geom, LinearRing):
        return subdivide_ring(geom)
    elif isinstance(geom, Polygon):
        return subdivide_polygon(geom)

    raise NotImplementedError(f"Subdivision for {type(geom)} not implemented")


def subdivide_line(line: LineString) -> LineString:
    half_point = line.interpolate(0.5, normalized=True)
    return shapely.LineString((line.coords[0], *half_point.coords, line.coords[-1]))


def subdivide_ring(ring: LinearRing) -> LinearRing:
    ring_segments = []
    for segment in pairs(list(ring.coords)):
        ring_segments.append(subdivide_line(LineString(segment)))

    return shapely.LinearRing(linemerge(ring_segments))


def subdivide_polygon(polygon: shapely.Polygon) -> shapely.Polygon:
    exterior = subdivide_ring(polygon.exterior)

    interiors = []
    for interior in polygon.interiors:
        interiors.append(subdivide_ring(interior))

    return Polygon(exterior, holes=interiors)


if __name__ == "__main__":

    def uihasud():
        from jord.shapely_utilities import dilate

        a = dilate(
            shapely.Point((0, 0)), distance=1, cap_style=shapely.BufferCapStyle.square
        )

        print(a.exterior)
        print(subdivide_ring(a.exterior))

    def uhasd():
        from jord.shapely_utilities import dilate

        a = dilate(
            shapely.Point((0, 0)), distance=1, cap_style=shapely.BufferCapStyle.square
        )
        b = dilate(
            shapely.Point((0, 0)), distance=0.5, cap_style=shapely.BufferCapStyle.square
        )
        c = a - b

        print(c)
        print(subdivide_polygon(c))

    uihasud()
    uhasd()
