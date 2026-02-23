from osgeo import osr

__all__ = ["get_spatial_reference_from_epsg"]


def get_spatial_reference_from_epsg(epsg_number: int) -> osr.SpatialReference:
    """

    :param epsg_number:
    :type epsg_number:
    :return:
    :rtype:
    """
    srs = osr.SpatialReference()
    res = srs.ImportFromEPSG(epsg_number)
    if res != 0:
        raise RuntimeError(f"{repr(res)}: could not import from EPSG")
    return srs
