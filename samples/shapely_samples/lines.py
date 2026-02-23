from shapely import MultiLineString

from jord.shapely_utilities import extend_lines


def uahsduhjasd():
    """ """
    print(extend_lines(MultiLineString([[[0, 0], [0, 1]], [[0, 2], [0, 3]]]), 1))

    print(extend_lines(MultiLineString([[[0, 0], [1, 0]], [[2, 0], [3, 0]]]), 1))


uahsduhjasd()
