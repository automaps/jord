__author__ = "heider"
__doc__ = r"""

           Created on 5/5/22
           """

from types import ModuleType

__all__ = ["import_gdal", "import_osr", "import_ogr", "GDAL", "OSR", "OGR"]


def import_gdal() -> ModuleType:
    """

    :return:
    :rtype:
    """
    try:
        import gdal

    except (ImportError, ModuleNotFoundError) as e:
        try:
            from osgeo import gdal
        except Exception as e2:
            raise ImportError(f"gdal is not installed {type(e), e, type(e2), e2}")

    gdal.UseExceptions()

    return gdal


def import_osr() -> ModuleType:
    """

    :return:
    :rtype:
    """
    try:
        import ors

    except (ImportError, ModuleNotFoundError) as e:
        try:
            from osgeo import osr
        except Exception as e2:
            raise ImportError(f"osr is not installed {type(e), e, type(e2), e2}")

    osr.UseExceptions()

    return osr


def import_ogr() -> ModuleType:
    """

    :return:
    :rtype:
    """
    try:
        import ogr

    except (ImportError, ModuleNotFoundError) as e:
        try:
            from osgeo import ogr
        except Exception as e2:
            raise ImportError(f"ogr is not installed {type(e), e, type(e2), e2}")

    ogr.UseExceptions()

    return ogr


GDAL = import_gdal()
OSR = import_osr()
OGR = import_ogr()
