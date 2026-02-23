from shapely import LineString

from jord.shapely_utilities.morphology import clean_shape


def ausdhasu2():
    """ """
    p = LineString([(1, 1), (1, 1)])
    print(clean_shape(p))


def ausdhasu3():
    """ """
    p = LineString(
        [
            [0.95876672850561, 0.41747472399753005],
            [0.95861672850561, 0.41747472399753005],
        ]
    )
    print(clean_shape(p))
    print(clean_shape(p, grid_size=1e-3))


ausdhasu3()
