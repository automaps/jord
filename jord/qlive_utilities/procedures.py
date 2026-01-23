import logging
import numpy
import shapely.geometry
import time
import tqdm
import uuid
from enum import Enum
from itertools import tee
from pandas import DataFrame
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union
from warg import Number, ensure_existence, passes_kws_to

from jord import PROJECT_APP_PATH
from jord.typing_utilities.type_solving import (
    solve_attribute_uri,
    solve_field_uri,
    to_string_if_not_of_exact_type,
)
from .layer_creation import (
    add_qgis_multi_feature_layer,
    add_qgis_single_feature_layer,
)
from .parsing import wkb_geom_constructor

APPEND_TIMESTAMP = True
SKIP_MEMORY_LAYER_CHECK_AT_CLOSE = True
PIXEL_SIZE = 1
DEFAULT_NUMBER = 0
CONTRAST_ENHANCE = True
DEFAULT_LAYER_NAME = "QliveLayer"
DEFAULT_LAYER_CRS = "EPSG:4326"
VERBOSE = False
STRICT = False

__all__ = [
    "add_raster",
    "add_rasters",
    "add_wkt",
    "add_wkts",
    "add_wkt_layer",
    "add_wkb",
    "add_wkbs",
    "add_wkb_layer",
    "add_dataframe",
    "add_dataframes",
    "add_dataframe_layer",
    "add_geojson",
    "add_geojsons",
    "add_geojson_layer",
    "add_shapely_geometry",
    "add_shapely_geometries",
    "add_shapely_layer",
    "add_no_geom_layer",
    "clear_all",
    "remove_layers",
    "remove_layer",
    "QliveRPCMethodEnum",
    "QliveRPCMethodMap",
]

_logger = logging.getLogger(__name__)


@passes_kws_to(add_qgis_single_feature_layer)
def add_wkb(qgis_instance_handle: Any, wkb: bytes, *args, **kwargs) -> List:
    """

    :param qgis_instance_handle:
    :param wkb:
    :param kwargs:
    :return:
    """
    # noinspection PyUnresolvedReferences
    from qgis.core import QgsGeometry

    return add_qgis_single_feature_layer(
        qgis_instance_handle, wkb_geom_constructor(wkb), *args, **kwargs
    )


@passes_kws_to(add_wkb)
def add_wkbs(
    qgis_instance_handle: Any, wkbs: Mapping[str, bytes], *args, **kwargs
) -> List:
    """

    :param qgis_instance_handle:
    :param wkbs:
    :param kwargs:
    :return:
    """
    return_list = []
    for layer_name, wkb in wkbs.items():
        return_list.extend(
            add_wkb(qgis_instance_handle, wkb, *args, name=layer_name, **kwargs)
        )
    return return_list


@passes_kws_to(add_qgis_multi_feature_layer)
def add_wkb_layer(
    qgis_instance_handle: Any, wkbs: Iterable[bytes], *args, **kwargs
) -> List:
    # noinspection PyUnresolvedReferences
    from qgis.core import QgsGeometry

    if isinstance(wkbs, bytes):
        wkbs = [wkbs]

    return add_qgis_multi_feature_layer(
        qgis_instance_handle,
        [wkb_geom_constructor(wkb) for wkb in wkbs],
        *args,
        **kwargs,
    )


@passes_kws_to(add_qgis_multi_feature_layer)
def add_geojson_layer(
    qgis_instance_handle: Any, geojsons: Iterable[str], *args, **kwargs
) -> List:
    """

      fromMultiPointXY

    Creates a new geometry from a QgsMultiPointXY object

    fromMultiPolygonXY

    Creates a new geometry from a QgsMultiPolygonXY.

    fromMultiPolylineXY

    Creates a new geometry from a QgsMultiPolylineXY object.

    fromPointXY

    Creates a new geometry from a QgsPointXY object

    fromPolygonXY

    Creates a new polygon geometry from a list of lists of QgsPointXY.

    fromPolyline

    Creates a new LineString geometry from a list of QgsPoint points.

    fromPolylineXY

    Creates a new LineString geometry from a list of QgsPointXY points.

    fromQPointF

    Construct geometry from a QPointF

    fromQPolygonF

    Construct geometry from a QPolygonF.

    fromRect

    Creates a new geometry from a QgsRectangle

    fromWkb

    Set the geometry, feeding in the buffer containing OGC Well-Known Binary

    fromWkt

    Creates a new geometry from a WKT string


    TODO: IMPLEMENT THIS

      :param qgis_instance_handle:
      :param wkbs:
      :param args:
      :param kwargs:
      :return:
    """
    # noinspection PyUnresolvedReferences
    from qgis.core import QgsGeometry

    return add_qgis_multi_feature_layer(
        qgis_instance_handle,
        # [gj for gj in geojsons],
        *args,
        **kwargs,
    )


@passes_kws_to(add_qgis_single_feature_layer)
def add_wkt(qgis_instance_handle: Any, wkt: str, *args, **kwargs) -> List:
    """

    :param qgis_instance_handle:
    :param wkt:
    :param kwargs:
    :return:
    """
    # noinspection PyUnresolvedReferences
    from qgis.core import QgsGeometry

    return add_qgis_single_feature_layer(
        qgis_instance_handle, QgsGeometry.fromWkt(wkt), *args, **kwargs
    )


@passes_kws_to(add_wkt)
def add_wkts(
    qgis_instance_handle: Any, wkts: Mapping[str, str], *args, **kwargs
) -> List:
    """

    :param qgis_instance_handle:
    :param wkts:
    :param kwargs:
    :return:
    """
    return_list = []
    for layer_name, wkt in wkts.items():
        return_list.extend(
            add_wkt(qgis_instance_handle, wkt, *args, name=layer_name, **kwargs)
        )
    return return_list


@passes_kws_to(add_qgis_multi_feature_layer)
def add_wkt_layer(
    qgis_instance_handle: Any, wkts: Iterable[str], *args, **kwargs
) -> List:
    # noinspection PyUnresolvedReferences
    from qgis.core import QgsGeometry

    if isinstance(wkts, str):
        wkts = [wkts]

    return add_qgis_multi_feature_layer(
        qgis_instance_handle,
        [QgsGeometry.fromWkt(wkt) for wkt in wkts],
        *args,
        **kwargs,
    )


@passes_kws_to(add_wkb)
def add_shapely_geometry(
    qgis_instance_handle: Any, geom: shapely.geometry.base.BaseGeometry, *args, **kwargs
) -> List:
    """
    Add a shapely geometry

    :param geom:
    :param qgis_instance_handle:
    :return:
    """
    # geom: shapely.geometry.base.BaseGeometry
    # assert geom.has_z, f"{geom=} does not have z"

    return add_wkb(qgis_instance_handle, geom.wkb, *args, **kwargs)


@passes_kws_to(add_shapely_geometry)
def add_shapely_geometries(
    qgis_instance_handle: Any, geometries: Mapping, *args, **kwargs
) -> None:
    """

    :param geometries:
    :param qgis_instance_handle:
    :param kwargs:
    :return:
    """
    for layer_name, geometry in geometries.items():
        add_shapely_geometry(
            qgis_instance_handle, geometry, name=layer_name, *args, **kwargs
        )


@passes_kws_to(add_wkb_layer)
def add_shapely_layer(
    qgis_instance_handle: Any,
    geoms: Iterable[shapely.geometry.base.BaseGeometry],
    *args,
    **kwargs,
) -> List:
    # assert geoms[0] == #TODO: SAME TYPE
    if isinstance(geoms, shapely.geometry.base.BaseGeometry):
        geoms = [geoms]

    return add_wkb_layer(
        qgis_instance_handle, [geom.wkb for geom in geoms], *args, **kwargs
    )


@passes_kws_to(add_wkb)  # OR add_wkt
def add_dataframe(
    qgis_instance_handle: Any,
    dataframe: DataFrame,
    geometry_column: str = "geometry",
    *args,
    **kwargs,
) -> List:
    """

    :param qgis_instance_handle:
    :param dataframe:
    :param kwargs:
    :return:
    """
    from geopandas import GeoDataFrame
    from jord.geopandas_utilities import split_on_geom_type

    return_list = []

    if isinstance(dataframe, GeoDataFrame):
        geom_dict = split_on_geom_type(dataframe)
        for df in geom_dict.values():
            if False:
                for w in df.geometry.to_wkb():  # .to_wkt(rounding_precision=-1):
                    return_list.append(
                        add_wkb(qgis_instance_handle, w, *args, **kwargs)
                    )
            else:
                for columns, w in zip(
                    df.iterrows(), df.geometry.to_wkb()
                ):  # TODO: ITERROWS may not work
                    return_list.append(
                        add_wkb(qgis_instance_handle, w, columns, *args, **kwargs)
                    )

    elif isinstance(dataframe, DataFrame):
        raise NotImplemented
        if isinstance(
            dataframe[geometry_column][0], shapely.geometry.base.BaseGeometry
        ):
            a = dataframe[geometry_column][0]
            # if a.geom_type == "MultiPolygon":

            wkts = [d.wkb for d in dataframe[geometry_column]]
        elif isinstance(dataframe[geometry_column][0], bytes):
            wkts = dataframe[geometry_column]
        elif isinstance(dataframe[geometry_column][0], str):
            wkts = dataframe[geometry_column]
        else:
            raise NotImplemented

        for row in wkts:
            return_list.append(add_wkb(qgis_instance_handle, row, *args, **kwargs))
    else:
        raise NotImplemented

    return return_list


@passes_kws_to(add_dataframe)
def add_dataframes(
    qgis_instance_handle: Any, dataframes: Mapping[str, DataFrame], *args, **kwargs
) -> List:
    return_list = []
    for layer_name, geometry in dataframes.items():
        return_list.append(
            add_dataframe(
                qgis_instance_handle, geometry, name=layer_name, *args, **kwargs
            )
        )
    return return_list


@passes_kws_to(add_wkb_layer)
def add_dataframe_layer(
    qgis_instance_handle: Any,
    dataframe: DataFrame,
    name: str = None,
    geometry_column="geometry",
    *args,
    **kwargs,
) -> List:
    from geopandas import GeoDataFrame
    from jord.geopandas_utilities import split_on_geom_type

    return_list = []

    if isinstance(dataframe, GeoDataFrame):
        total_feature_len = len(dataframe)
        split_accum_len = 0
        accum_feature_len = 0
        geom_dict = split_on_geom_type(dataframe)

        append_type_name = False

        if len(geom_dict) > 1:  # Must be split
            append_type_name = True
            if (
                name is None
            ):  # if No name give one to have some commonness of new layers in names
                name = DEFAULT_LAYER_NAME
                if APPEND_TIMESTAMP and False:
                    name += f"_{time.time()}"

        for k, df in geom_dict.items():  # each geom type
            geoms = []
            columns = []

            assert len(df) == len(df.geometry)
            # logger.info(f"{name=} has {len(df.geometry)} {k.value} geometries")

            for (i, c), w in zip(
                df.iterrows(), df.geometry.to_wkb()  # .to_wkt(rounding_precision=-1)
            ):
                c.pop(geometry_column)
                geoms.append(w)
                columns.append({**c})
                split_accum_len += 1

            if append_type_name:
                layer_name = f"{name}_{k.name}"
            else:
                layer_name = name

            if geoms:
                added_layers = add_wkb_layer(
                    qgis_instance_handle,
                    geoms,
                    name=layer_name,
                    columns=columns,
                    *args,
                    **kwargs,
                )

                assert added_layers is not None, f"{added_layers=} must not be None"
                for al in added_layers:
                    accum_feature_len += al.featureCount()

                return_list.extend(added_layers)

    elif isinstance(dataframe, DataFrame):
        raise NotImplemented
        geom_dict = split_on_geom_type(dataframe)
        for df in geom_dict.values():  # each geom type
            geoms = []
            columns = []
            for (i, c), w in zip(
                df.iterrows(), df.geometry.to_wkb()  # .to_wkt(rounding_precision=-1)
            ):
                c.pop(geometry_column)
                geoms.append(w)
                columns.append({**c})

            return_list.append(
                add_wkb_layer(
                    qgis_instance_handle, geoms, columns=columns, *args, **kwargs
                )
            )

    else:
        raise NotImplemented(f"{type(dataframe)}, {dataframe}")

    if STRICT:
        assert (
            total_feature_len == split_accum_len
        ), f"only iterated {split_accum_len}/{total_feature_len=} of geometries"
        assert (
            total_feature_len == accum_feature_len
        ), f"only added {accum_feature_len}/{total_feature_len=} of geometries"
    else:
        if total_feature_len != split_accum_len:
            _logger.error(
                f"only iterated {split_accum_len}/{total_feature_len=} of geometries"
            )
        if total_feature_len != accum_feature_len:
            _logger.error(
                f"only added {accum_feature_len}/{total_feature_len=} of geometries"
            )

    return return_list


@passes_kws_to(add_shapely_geometry)
def add_geojson(qgis_instance_handle: Any, geojson_: str, *args, **kwargs) -> List:
    """

    :param geojson_:
    :param qgis_instance_handle:
    :param kwargs:
    :return:
    """
    # meta_data = ''
    return add_shapely_geometry(
        qgis_instance_handle, shapely.from_geojson(geojson_), *args, **kwargs
    )


@passes_kws_to(add_shapely_geometry)
def add_geojsons(
    qgis_instance_handle: Any, geojsons: Mapping[str, str], *args, **kwargs
) -> List:
    """

    :param qgis_instance_handle:
    :param geojsons:
    :param kwargs:
    :return:
    """
    return_list = []
    for layer_name, geojson_ in geojsons.items():
        return_list.append(
            add_shapely_geometry(
                qgis_instance_handle,
                shapely.from_geojson(geojson_),
                name=layer_name,
                *args,
                **kwargs,
            )
        )
    return return_list


@passes_kws_to(add_shapely_layer)
def add_geojson_layer(
    qgis_instance_handle: Any, geojsons: Iterable[str], *args, **kwargs
) -> List:
    if isinstance(geojsons, str):
        geojsons = [geojsons]

    return add_shapely_layer(
        qgis_instance_handle,
        [shapely.from_geojson(geojson_) for geojson_ in geojsons],
        *args,
        **kwargs,
    )


def remove_layers(qgis_instance_handle: Any, *args) -> None:
    """
    clear all the added layers

    :param qgis_instance_handle:
    :param args:
    :return: None
    :rtype: None
    """
    qgis_instance_handle.on_clear_temporary()


def remove_layer(qgis_instance_handle: Any, name: str, *args) -> None:
    ...
    # qgis_instance_handle.on_clear_temporary()


def clear_all(qgis_instance_handle: Any, *args) -> None:  # TODO: REMOVE THIS!
    """
    clear all the added layers

    :param qgis_instance_handle:
    :return:
    """
    remove_layers(qgis_instance_handle)
    if VERBOSE:
        print("CLEAR ALL!")


def add_raster(
    qgis_instance_handle: Any,
    raster: numpy.ndarray,
    name: str = DEFAULT_LAYER_NAME,
    centroid: Tuple[Number, Number] = None,
    extent_tuple: Tuple[Number, Number, Number, Number] = None,
    pixel_size: Tuple[Number, Number] = PIXEL_SIZE,
    crs_str: str = DEFAULT_LAYER_CRS,
    default_value: Number = DEFAULT_NUMBER,
    field: str = None,
    no_data_value: int = -1,
    group: Any = None,
    visible: bool = True,
) -> List:
    """
    add a raster

    :param group:
    :param visible:
    :param no_data_value:
    :param qgis_instance_handle:
    :param raster:
    :param name:
    :param centroid:
    :param extent_tuple:
    :param pixel_size:
    :param crs_str:
    :param default_value:
    :param field:
    :return: None
    :rtype: None
    """
    # noinspection PyUnresolvedReferences
    from qgis.core import (
        QgsRectangle,
        QgsCoordinateReferenceSystem,
        QgsRasterBandStats,
        QgsSingleBandGrayRenderer,
        QgsMultiBandColorRenderer,
        QgsContrastEnhancement,
        QgsRasterLayer,
        QgsRasterFileWriter,
        Qgis,
    )
    from jord.qgis_utilities.numpy_utilities.data_type import get_qgis_type
    from jord.qgis_utilities.helpers.sessions import RasterDataProviderEditSession

    x_size, y_size, *rest_size = raster.shape

    if len(rest_size) == 0:
        raster = numpy.expand_dims(raster, axis=-1)

    *_, num_bands = raster.shape

    data_type = get_qgis_type(raster.dtype).value

    # QgsWkbTypes.displayString(gPolygon.wkbType())

    extent = QgsRectangle()

    if extent_tuple:
        extent.setXMinimum(extent_tuple[0])
        extent.setYMinimum(extent_tuple[1])
        extent.setXMaximum(extent_tuple[2])
        extent.setYMaximum(extent_tuple[3])
    else:
        raster_half_size = (PIXEL_SIZE * (x_size / 2.0), PIXEL_SIZE * (y_size / 2.0))

        raster_half_size = raster_half_size[1], raster_half_size[0]

        if centroid is None:
            centroid = (0, 0)  # raster_half_size

        extent.setXMinimum(centroid[0] - raster_half_size[0])
        extent.setXMaximum(centroid[0] + raster_half_size[0])

        extent.setYMinimum(centroid[1] - raster_half_size[1])
        extent.setYMaximum(centroid[1] + raster_half_size[1])

    if APPEND_TIMESTAMP:
        name += f"_{time.time()}"

    temp_file = (
        ensure_existence(PROJECT_APP_PATH.user_data / "rasters") / f"{uuid.uuid4()}.tif"
    )
    writer = QgsRasterFileWriter(str(temp_file))

    if num_bands > 1:
        provider = writer.createMultiBandRaster(
            dataType=data_type,
            width=x_size,
            height=y_size,
            extent=extent,
            crs=QgsCoordinateReferenceSystem(crs_str),
            nBands=num_bands,
        )
    else:
        provider = writer.createOneBandRaster(
            dataType=data_type,
            width=x_size,
            height=y_size,
            extent=extent,
            crs=QgsCoordinateReferenceSystem(crs_str),
        )

    w_pixels, h_pixels = (
        x_size,
        y_size,
    )  # TODO: FIGURE OUT HOW TO HANDLE NON SQUARE RASTERS! SCALE DIMS BY SOME AMOUNT.

    with RasterDataProviderEditSession(provider):
        progress = range(0, num_bands)

        if VERBOSE:
            progress = tqdm.tqdm(progress)

        for ith_band in progress:
            block = provider.block(
                bandNo=ith_band + 1, boundingBox=extent, width=w_pixels, height=h_pixels
            )
            provider.setNoDataValue(bandNo=ith_band + 1, noDataValue=no_data_value)

            for wp in range(0, w_pixels):
                for hp in range(0, h_pixels):
                    value = raster[wp][hp][ith_band]
                    if value == numpy.nan:
                        if block.setIsNoData(wp, hp):
                            continue
                    block.setValue(wp, hp, value)

            if VERBOSE:
                print("writing block on band", ith_band + 1)

            provider.writeBlock(block, band=ith_band + 1, xOffset=0, yOffset=0)

            del block

    layer = QgsRasterLayer(str(temp_file), name, "gdal")

    if num_bands == 1:
        # this is needed for the min and max value to refresh in the layer panel
        renderer = layer.renderer()

        gray_renderer = QgsSingleBandGrayRenderer(provider, 1)

        if CONTRAST_ENHANCE:
            stats = provider.bandStatistics(1, QgsRasterBandStats.All, extent)
            min_value = stats.minimumValue
            max_value = stats.maximumValue

            my_enhancement = QgsContrastEnhancement()
            my_enhancement.setContrastEnhancementAlgorithm(
                QgsContrastEnhancement.StretchToMinimumMaximum, True
            )
            my_enhancement.setMinimumValue(min_value)
            my_enhancement.setMaximumValue(max_value)
            gray_renderer.setContrastEnhancement(my_enhancement)

        layer.setRenderer(gray_renderer)

    elif num_bands != 4:
        multi_color_renderer = QgsMultiBandColorRenderer(provider, 1, 2, 3)

        layer.setRenderer(multi_color_renderer)
        layer.setDefaultContrastEnhancement()
        layer.triggerRepaint()
        # iface.legendInterface().refreshLayerSymbology(layer)

    else:
        multi_color_renderer = QgsMultiBandColorRenderer(provider, 1, 2, 3)

        layer.setRenderer(multi_color_renderer)
        layer.setDefaultContrastEnhancement()
        layer.triggerRepaint()

    if SKIP_MEMORY_LAYER_CHECK_AT_CLOSE:
        layer.setCustomProperty("skipMemoryLayersCheck", 1)

    if group:
        qgis_instance_handle.qgis_project.addMapLayer(layer, False)
        group.insertLayer(0, layer)
    else:
        qgis_instance_handle.qgis_project.addMapLayer(layer)

    layer_tree_handle = qgis_instance_handle.qgis_project.layerTreeRoot().findLayer(
        layer.id()
    )
    if layer_tree_handle:
        layer_tree_handle.setItemVisibilityChecked(visible)

    return [layer]


@passes_kws_to(add_raster, no_pass_filter=["name"])
def add_rasters(qgis_instance_handle: Any, rasters: Mapping, *args, **kwargs) -> List:
    """

    :param qgis_instance_handle:
    :param rasters:
    :param kwargs:
    :return:
    """
    return_list = []
    for layer_name, raster in rasters.items():
        return_list.append(
            add_raster(qgis_instance_handle, raster, *args, name=layer_name, **kwargs)
        )

    return return_list


def add_no_geom_layer(
    qgis_instance_handle: Any,
    columns: Optional[
        Union[Mapping[str, Mapping[str, Any]], Iterable[Mapping[str, Any]]]
    ],
    name: Optional[Iterable[str]] = None,
    index: bool = False,
    group: Any = None,
    visible: bool = True,
) -> Optional[List]:
    """

        fields  == column definition name, type, length/size
        Multiple field parameters can be added to the data provider definition. type is one of “integer”,
        “double”, “string”.

    An example url is “Point?crs=epsg:4326&field=id:integer&field=name:string(20)&index=yes”


    :param visible:
    :param group:
    :param qgis_instance_handle:
    :param name:
    :param columns:
    :param index:
    :return:
    """

    # noinspection PyUnresolvedReferences
    from qgis.core import QgsFeature, QgsVectorLayer, QgsProject, QgsFeatureSink

    # noinspection PyUnresolvedReferences
    import qgis

    return_collection = []

    if name is None:
        name = DEFAULT_LAYER_NAME

    crs = None
    if crs is None:
        crs = DEFAULT_LAYER_CRS

    layer_name = f"{name}"
    if APPEND_TIMESTAMP:
        layer_name += f"_{time.time()}"

    uri = "None"

    num_cols = None
    attr_generator = None
    fields = None
    field_type_configuration = None

    if columns and len(columns):  # TODO: FIND MAX LENGTH STR
        if isinstance(columns, Mapping):
            attr_generator, attr_type_sampler = tee(iter(columns.values()))
        elif isinstance(columns, Iterable):
            attr_generator, attr_type_sampler = tee(iter(columns))
        else:
            raise TypeError(f"columns must be a mapping or an iterable of mappings")

        field_type_configuration, fields, num_cols = solve_attribute_uri(
            attr_type_sampler, columns
        )

    features = []
    for row in attr_generator:
        if row is not None:
            feat = QgsFeature()
            feat.initAttributes(num_cols)
            feat.setAttributes(list(to_string_if_not_of_exact_type(row.values())))

            assert feat.isValid(), f"{feat} was invalid"
            features.append(feat)

    uri += "?"

    if crs:
        uri += f"crs={crs}"

    if fields:  # field=name:type(length,precision)
        uri = solve_field_uri(field_type_configuration, fields, uri)

    uri = str(uri).rstrip("&")
    uri += f'&index={"yes" if index else "no"}'
    uri.replace("?&", "?")

    layer = QgsVectorLayer(uri, layer_name, "memory")
    layer_data_provider = layer.dataProvider()
    # pr.addAttributes([QgsField("name", QVariant.String),QgsField("age", QVariant.Int),QgsField("size",
    # QVariant.Double)])

    (res, out_feats) = layer_data_provider.addFeatures(
        features
        # , QgsFeatureSink.RollBackOnErrors
    )

    if not res:
        _logger.error(f"{layer_data_provider.lastError()}")

        assert (
            res
        ), f"Failure while adding features {res} {layer_data_provider.lastError()}"

    layer_data_provider.updateExtents()

    if SKIP_MEMORY_LAYER_CHECK_AT_CLOSE:
        layer.setCustomProperty("skipMemoryLayersCheck", 1)

    layer.commitChanges()
    layer.updateFields()
    layer.updateExtents()

    if qgis_instance_handle is None:
        qgis_project = QgsProject.instance()
    elif not isinstance(qgis_instance_handle, QgsProject):
        qgis_project = qgis_instance_handle.qgis_project
    else:
        qgis_project = qgis_instance_handle

    if group:
        qgis_project.addMapLayer(layer, False)
        group.insertLayer(0, layer)
    else:
        qgis_project.addMapLayer(layer)

    layer_tree_handle = qgis_project.layerTreeRoot().findLayer(layer.id())
    if layer_tree_handle:
        layer_tree_handle.setItemVisibilityChecked(visible)

    actions = qgis.utils.iface.layerTreeView().defaultActions()
    actions.showFeatureCount()  # TODO: Twice?
    actions.showFeatureCount()

    return_collection.append(layer)

    assert len(return_collection) > 0, f"Return collection was empty"

    return return_collection


class QliveRPCMethodEnum(Enum):
    # add_layers = add_layers.__name__

    remove_layers = remove_layers.__name__
    clear_all = clear_all.__name__
    remove_layer = remove_layer.__name__

    add_wkt = add_wkt.__name__
    add_wkts = add_wkts.__name__
    add_wkt_layer = add_wkt_layer.__name__

    add_wkb = add_wkb.__name__
    add_wkbs = add_wkbs.__name__
    add_wkb_layer = add_wkb_layer.__name__

    add_dataframe = add_dataframe.__name__
    add_dataframes = add_dataframes.__name__
    add_dataframe_layer = add_dataframe_layer.__name__

    add_shapely_geometry = add_shapely_geometry.__name__
    add_shapely_geometries = add_shapely_geometries.__name__
    add_shapely_layer = add_shapely_layer.__name__

    add_geojson = add_geojson.__name__
    add_geojsons = add_geojsons.__name__
    add_geojson_layer = add_geojson_layer.__name__

    add_raster = add_raster.__name__
    add_rasters = add_rasters.__name__

    add_no_geom_layer = add_no_geom_layer.__name__


funcs = locals()  # In local scope for name
QliveRPCMethodMap = {e: funcs[e.value] for e in QliveRPCMethodEnum}
