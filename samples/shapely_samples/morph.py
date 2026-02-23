import shapely
from shapely import LineString, LinearRing, Point
from shapely.geometry import Polygon

from jord.shapely_utilities import closing, dilate, erode, opening
from jord.shapely_utilities.morphology import pro_closing, pro_opening

point = Point([(0.0, 0.0)])
line = LineString([(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)])
poly = Polygon([(0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25)])

print(point.buffer(1, cap_style="flat"))  # WHA
print(line.buffer(1, cap_style="flat"))
print(poly.buffer(1, cap_style="flat"))

print(point.buffer(-1, cap_style="flat"))
print(line.buffer(-1, cap_style="flat"))
print(poly.buffer(-1, cap_style="flat"))

print(point.buffer(1, cap_style=shapely.BufferCapStyle.square))

if __name__ == "__main__":

    def aishdjauisd():
        """ """
        # Import constructors for creating geometry collections
        from shapely.geometry import MultiPoint, MultiLineString

        # Import necessary geometric objects from shapely module
        from shapely.geometry import Point, LineString, Polygon

        # Create Point geometric object(s) with coordinates
        point1 = Point(2.2, 4.2)
        point2 = Point(7.2, -25.1)
        point3 = Point(9.26, -2.456)
        # point3D = Point(9.26, -2.456, 0.57)

        # Create a MultiPoint object of our points 1,2 and 3
        multi_point = MultiPoint([point1, point2, point3])

        # It is also possible to pass coordinate tuples inside
        multi_point2 = MultiPoint([(2.2, 4.2), (7.2, -25.1), (9.26, -2.456)])

        # We can also create a MultiLineString with two lines
        line1 = LineString([point1, point2])
        line2 = LineString([point2, point3])
        multi_line = MultiLineString([line1, line2])
        polygon = Polygon([point2, point1, point3])

        from shapely.geometry import GeometryCollection
        from matplotlib import pyplot
        import geopandas

        geoms = GeometryCollection([multi_point, multi_point2, multi_line, polygon])

        # A positive distance produces a dilation, a negative distance an erosion. A very small or zero distance
        # may sometimes be used to “tidy” a polygon.
        geoms = opening(geoms)
        geoms = dilate(geoms)
        geoms = closing(geoms)
        geoms = erode(geoms)

        p = geopandas.GeoSeries(geoms)
        p.plot()
        pyplot.show()

    def ahfuashdu():
        """ """
        from random import random
        import matplotlib.pyplot
        import geopandas

        circle_diameter = 100.0
        ring_width = 6.0

        circle = dilate(shapely.Point(0, 0), distance=circle_diameter)
        ring = circle.difference(erode(circle, distance=ring_width))

        noise_elements = []

        num_noise_points = 1000
        num_noise_lines = 100
        noise_amplitude = 2.0

        for i in range(num_noise_points):
            noise_elements.append(
                dilate(
                    shapely.Point(
                        -circle_diameter + random() * circle_diameter * 2,
                        -circle_diameter + random() * circle_diameter * 2,
                    ),
                    distance=random() * noise_amplitude,
                )
            )

        for i in range(num_noise_lines):
            noise_elements.append(
                dilate(
                    shapely.LineString(
                        [
                            shapely.Point(
                                -circle_diameter + random() * circle_diameter * 2,
                                -circle_diameter + random() * circle_diameter * 2,
                            )
                            for _ in range(2)
                        ]
                    ),
                    distance=random() * noise_amplitude,
                )
            )

        noisy_ring = shapely.unary_union(noise_elements + [ring])

        geopandas.GeoSeries(noisy_ring).plot()
        matplotlib.pyplot.title("noisy_ring")
        matplotlib.pyplot.show()

        some_ring = opening(noisy_ring, distance=noise_amplitude)

        geopandas.GeoSeries(some_ring).plot()
        matplotlib.pyplot.title("opening_ring")
        matplotlib.pyplot.show()

        some_ring = closing(
            opening(noisy_ring, distance=noise_amplitude), distance=noise_amplitude
        )

        geopandas.GeoSeries(some_ring).plot()
        matplotlib.pyplot.title("some_ring")
        matplotlib.pyplot.show()

        pro_closing_ring = pro_closing(noisy_ring, distance=noise_amplitude)

        geopandas.GeoSeries(pro_closing_ring).plot()
        matplotlib.pyplot.title("pro_closing_ring")
        matplotlib.pyplot.show()

        pro_opening_ring = pro_opening(noisy_ring, distance=noise_amplitude)

        geopandas.GeoSeries(pro_opening_ring).plot()
        matplotlib.pyplot.title("pro_opening_ring")
        matplotlib.pyplot.show()

    def ahfuas3232hdu():
        """ """
        lr = LinearRing([(-1, -1), (1, 1), (1, 1), (1, -1), (-1, -1)])
        print(dilate(lr))
        print(lr.buffer(0))

    def simple_dilate_example():
        """ """
        print(dilate(shapely.Point(0, 0)))
        print(dilate(shapely.Point(0, 0), distance=0))

    simple_dilate_example()
    # ahfuas3232hdu()
    # ahfuashdu()
    # aishdjauisd()
