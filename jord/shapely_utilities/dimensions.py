import shapely


def add_polygon_z(polygon_2d, z_s):
    """

    :param polygon_2d:
    :type polygon_2d:
    :param z_s:
    :type z_s:
    :return:
    :rtype:
    """
    poly_exterior_s = polygon_2d.exterior.coords[:-1]
    assert len(poly_exterior_s) == len(z_s), (len(poly_exterior_s), len(z_s))

    polygon_3d = shapely.Polygon(
        [(x, y, z) for (x, y), z in zip(poly_exterior_s, z_s, strict=True)]
    )

    return polygon_3d


def add_linestring_z(linestring_2d, z_s):
    """

    :param linestring_2d:
    :type linestring_2d:
    :param z_s:
    :type z_s:
    :return:
    :rtype:
    """
    linestring_s = linestring_2d.coords
    assert len(linestring_s) == len(z_s), (len(linestring_s), len(z_s))

    linestring_3d = shapely.LineString(
        [(x, y, z) for (x, y), z in zip(linestring_s, z_s, strict=True)]
    )

    return linestring_3d


def add_point_z(point_2d, z):
    """

    :param point_2d:
    :type point_2d:
    :param z:
    :type z:
    :return:
    :rtype:
    """
    return shapely.Point([point_2d.x, point_2d.y, z])


def add_multipoint_z(multipoint_2d, z_s):
    """

    :param multipoint_2d:
    :type multipoint_2d:
    :param z_s:
    :type z_s:
    :return:
    :rtype:
    """
    return shapely.MultiPoint(
        [(x, y, z) for (x, y), z in zip(multipoint_2d, z_s, strict=True)]
    )


def add_multilinestring_z(multilinestring_2d, z_s):
    """

    :param multilinestring_2d:
    :type multilinestring_2d:
    :param z_s:
    :type z_s:
    :return:
    :rtype:
    """
    return shapely.MultiLineString(
        [
            [(x, y, z) for (x, y), z in zip(linestring.coords, z_s, strict=True)]
            for linestring in multilinestring_2d
        ]
    )


def add_multipolygon_z(multipolygon_2d, z_s):
    """

    :param multipolygon_2d:
    :type multipolygon_2d:
    :param z_s:
    :type z_s:
    :return:
    :rtype:
    """
    return shapely.MultiPolygon(
        [
            [
                [
                    (x, y, z)
                    for (x, y), z in zip(polygon.exterior.coords, z_s, strict=True)
                ]
                for polygon in multipolygon_2d
            ]
        ]
    )


def add_geometrycollection_z(geometrycollection_2d, z_s):
    """

    :param geometrycollection_2d:
    :type geometrycollection_2d:
    :param z_s:
    :type z_s:
    :return:
    :rtype:
    """
    return shapely.GeometryCollection(
        [
            add_geometry_z(geometry, z)
            for geometry, z in zip(geometrycollection_2d, z_s, strict=True)
        ]
    )


def add_geometry_z(geometry, z):
    """

    :param geometry:
    :type geometry:
    :param z:
    :type z:
    :return:
    :rtype:
    """
    if isinstance(geometry, shapely.geometry.Point):
        return add_point_z(geometry, z)
    elif isinstance(geometry, shapely.geometry.LineString):
        return add_linestring_z(geometry, z)
    elif isinstance(geometry, shapely.geometry.Polygon):
        return add_polygon_z(geometry, z)
    elif isinstance(geometry, shapely.geometry.MultiPoint):
        return add_multipoint_z(geometry, z)
    elif isinstance(geometry, shapely.geometry.MultiLineString):
        return add_multilinestring_z(geometry, z)
    elif isinstance(geometry, shapely.geometry.MultiPolygon):
        return add_multipolygon_z(geometry, z)
    elif isinstance(geometry, shapely.geometry.GeometryCollection):
        return add_geometrycollection_z(geometry, z)
    else:
        raise NotImplementedError(geometry)


def strip_z(geometry):  # TODO: IMPLEMENT
    """

    :param geometry:
    :type geometry:
    :return:
    :rtype:
    """
    if isinstance(geometry, shapely.geometry.Point):
        return shapely.Point([geometry.x, geometry.y])
    elif isinstance(geometry, shapely.geometry.LineString):
        return shapely.LineString(geometry.coords.xy)
    elif isinstance(geometry, shapely.geometry.Polygon):
        return shapely.Polygon(geometry.exterior.coords.xy)
    elif isinstance(geometry, shapely.geometry.MultiPoint):
        return shapely.MultiPoint([point.coords.xy for point in geometry])
    elif isinstance(geometry, shapely.geometry.MultiLineString):
        return shapely.MultiLineString(
            [linestring.coords.xy for linestring in geometry]
        )
    elif isinstance(geometry, shapely.geometry.MultiPolygon):
        return shapely.MultiPolygon(
            [polygon.exterior.coords.xy for polygon in geometry]
        )
    elif isinstance(geometry, shapely.geometry.GeometryCollection):
        return shapely.GeometryCollection([strip_z(geometry) for geometry in geometry])
    else:
        raise NotImplementedError(geometry)


if __name__ == "__main__":

    def iuasjhd():
        """ """
        print(
            add_polygon_z(
                shapely.geometry.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), [0, 1, 2, 3]
            )
        )

        print(add_linestring_z(shapely.geometry.LineString([(0, 0), (1, 1)]), [0, 1]))

        print(add_point_z(shapely.geometry.Point([0, 0]), 0))

        # print(strip_z(add_polygon_z(shapely.geometry.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), [0, 1, 2, 3])))

    iuasjhd()
