__author__ = "Christian Heider Lindbjerg"

import pytest
from warg import ensure_in_sys_path, find_nearest_ancestral_relative

ensure_in_sys_path(find_nearest_ancestral_relative("jord").parent)


def test_import_package():
    if True:
        import jord

        print(jord.__version__)


@pytest.mark.skipif(True, reason="Only with qgis present")
def test_qgis_import_package():
    if True:
        from jord import qgis_utilities

        print(qgis_utilities.__doc__)


def test_gdal_import_package():
    if False:
        print(gdal_utilities.__doc__)


@pytest.mark.skipif(True, reason="Only with qgis present")
def test_qlive_import_package():
    if True:
        from jord import qlive_utilities

        print(qlive_utilities.__doc__)


def test_geopandas_import_package():
    if True:
        from jord import geopandas_utilities

        print(geopandas_utilities.__doc__)


def test_geojson_import_package():
    if True:
        from jord import geojson_utilities

        print(geojson_utilities.__doc__)


def test_pillow_import_package():
    if True:
        from jord import pillow_utilities

        print(pillow_utilities.__doc__)


def test_qt_import_package():
    if False:
        print(qt_utilities.__doc__)


def test_pil_import_package():
    if True:
        from jord import pillow_utilities

        print(pillow_utilities.__doc__)


def test_shapely_import_package():
    if True:
        from jord import shapely_utilities

        print(shapely_utilities.__doc__)


def test_rasterio_import_package():
    if True:
        from jord import rasterio_utilities

        print(rasterio_utilities.__doc__)


def test_torch_import_package():
    if False:
        print(torch_utilities.__doc__)


if __name__ == "__main__":
    test_gdal_import_package()
    test_pil_import_package()
    test_gdal_import_package()
    test_import_package()
    test_shapely_import_package()
    test_rasterio_import_package()
    test_qgis_import_package()
