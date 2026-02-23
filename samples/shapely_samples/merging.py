def asudhua():
    """ """
    from shapely.ops import polygonize, polygonize_full

    lines = [
        ((0, 0), (1, 1)),
        ((0, 0), (0, 1)),
        ((0, 1), (1, 1)),
        ((1, 1), (1, 0)),
        ((1, 0), (0, 0)),
    ]
    list(polygonize(lines))

    lines = [
        ((0, 0), (1, 1)),
        ((0, 0), (0, 1)),
        ((0, 1), (1, 1)),
        ((1, 1), (1, 0)),
        ((1, 0), (0, 0)),
        ((5, 5), (6, 6)),
        ((1, 1), (100, 100)),
    ]
    result, cuts, dangles, invalids = polygonize_full(lines)
