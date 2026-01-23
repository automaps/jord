import logging
import time
from itertools import tee
from typing import Any, Callable, Iterable, List, Mapping, Optional, Union
from warg import TripleNumber, n_uint_mix_generator_builder, passes_kws_to

from jord.typing_utilities.type_solving import (
    solve_attribute_uri,
    solve_field_uri,
    solve_qgis_type,
    solve_type_configuration,
    to_string_if_not_of_exact_type,
)

APPEND_TIMESTAMP = True
SKIP_MEMORY_LAYER_CHECK_AT_CLOSE = True
PIXEL_SIZE = 1
DEFAULT_NUMBER = 0
CONTRAST_ENHANCE = True
DEFAULT_LAYER_NAME = "TemporaryLayer"
DEFAULT_LAYER_CRS = "EPSG:4326"
VERBOSE = False
STRICT = False  # TODO: SET TO TRUE!
USE_TEMP_GROUP = False

__all__ = [
    "add_qgis_single_feature_layer",
    "add_qgis_single_geometry_layers",
    "add_qgis_multi_feature_layer",
]

_logger = logging.getLogger(__name__)


def add_qgis_single_feature_layer(
    qgis_instance_handle: Optional[Any],
    geom: Any,  #: QgsGeometry,
    name: Optional[str] = None,
    crs: Optional[str] = None,
    columns: Optional[Mapping[str, Any]] = None,
    index: bool = False,
    categorise_by_attribute: Optional[str] = None,
    color_generator: Callable[[], TripleNumber] = n_uint_mix_generator_builder(
        255, 255, 255, mix_min=(222, 222, 222)
    ),
    group: Any = None,
    visible: bool = True,
    opacity: float = 1.0,
    measurements: Optional[Iterable[Iterable[float]]] = None,
) -> List:
    """
    An example url is “Point?crs=epsg:4326&field=id:integer&field=name:string(20)&index=yes”

    :param opacity:
    :param color_generator:
    :param visible:
    :param categorise_by_attribute:
    :param group:
    :param columns: Field=name:type(length,precision) Defines an attribute of the layer. Multiple field
    parameters can be added to the data provider definition. Type is one of “integer”, “double”, “string”.
    :param index: index=yes Specifies that the layer will be constructed with a spatial index
    :param qgis_instance_handle:
    :param geom:
    :type geom: QgsGeometry
    :param name:
    :type name: Optional[str]
    :param crs: Crs=definition Defines the coordinate reference system to use for the layer. Definition is any
    string accepted by QgsCoordinateReferenceSystem.createFromString()
    :param measurements: UNUSED!
    :return: None
    :rtype: None
    """
    # noinspection PyUnresolvedReferences
    from qgis.core import (
        QgsVectorLayer,
        QgsFeature,
        QgsVectorLayer,
        QgsRasterLayer,
        QgsProject,
        QgsWkbTypes,
    )
    from jord.qgis_utilities import categorise_layer

    # noinspection PyUnresolvedReferences
    import qgis

    # uri = geom.type()
    # uri = geom.wkbType()
    # uri = geom.wktTypeStr()

    return_collection = []

    if geom.wkbType() == QgsWkbTypes.NoGeometry:
        return return_collection

    geom_type = QgsWkbTypes.displayString(geom.wkbType())

    if True:
        _logger.error(f"{geom},{geom_type=}")

    uri = geom_type  # TODO: URI MIGHT BE NONE?

    if name is None:
        name = DEFAULT_LAYER_NAME

    if crs is None:
        crs = DEFAULT_LAYER_CRS

    layer_name = f"{name}"
    if APPEND_TIMESTAMP:
        layer_name += f"_{time.time()}"

    if columns:
        fields = {k: solve_qgis_type(v) for k, v in columns}
        field_type_configuration = {
            k: solve_type_configuration(v, k, columns) for k, v in columns.items()
        }
    else:
        fields = None
        field_type_configuration = None

    if categorise_by_attribute and fields:
        assert (
            categorise_by_attribute in fields
        ), f"{categorise_by_attribute} was not found in {fields}"

    if qgis_instance_handle is None:
        qgis_project = QgsProject.instance()
    elif not isinstance(qgis_instance_handle, QgsProject):
        qgis_project = qgis_instance_handle.qgis_project
    else:
        qgis_project = qgis_instance_handle

    if geom_type in (
        QgsWkbTypes.GeometryCollection,
        QgsWkbTypes.GeometryCollectionZ,
        QgsWkbTypes.GeometryCollectionM,
        QgsWkbTypes.GeometryCollectionZM,
    ):
        for g in geom.asGeometryCollection():  # TODO: Look into recursion?
            uri = QgsWkbTypes.displayString(g.wkbType())

            if True:
                _logger.error(f"{g},{uri=}")

            sub_type = uri  # TODO: URI MIGHT BE NONE?

            uri += "?"

            if crs:
                uri += f"crs={crs}"

            if fields:
                uri = str(uri).rstrip("&")
                for k, v in fields.items():
                    uri += f"&field={k}:{v}"

            uri = str(uri).rstrip("&")
            uri += f'&index={"yes" if index else "no"}'
            uri.replace("?&", "?")

            feat = QgsFeature()
            feat.setGeometry(g)

            if columns:
                feat.initAttributes(len(columns))

                if STRICT:
                    for field_idx, attr in enumerate(columns.values()):
                        feat.setAttribute(field_idx, attr)
                else:
                    feat.setAttributes(
                        list(to_string_if_not_of_exact_type(columns.values()))
                    )

            sub_layer = QgsVectorLayer(uri, f"{layer_name}_{sub_type}", "memory")
            layer_data_provider = sub_layer.dataProvider()
            layer_data_provider.addFeatures([feat])
            layer_data_provider.updateExtents()

            if SKIP_MEMORY_LAYER_CHECK_AT_CLOSE:
                sub_layer.setCustomProperty("skipMemoryLayersCheck", 1)

            if categorise_by_attribute:
                categorise_layer(
                    sub_layer,
                    categorise_by_attribute,
                    color_iterable=color_generator,
                    opacity=opacity,
                )

            sub_layer.commitChanges()
            sub_layer.updateFields()
            sub_layer.updateExtents()

            return_collection.append(sub_layer)

            if group:
                qgis_project.addMapLayer(sub_layer, False)
                group.insertLayer(0, sub_layer)
            else:
                qgis_project.addMapLayer(sub_layer)

            layer_tree_handle = qgis_project.layerTreeRoot().findLayer(sub_layer.id())
            if layer_tree_handle:
                layer_tree_handle.setItemVisibilityChecked(visible)
    else:
        uri += "?"

        if crs:
            uri += f"crs={crs}"

        if fields:
            uri = solve_field_uri(field_type_configuration, fields, uri)

        uri = str(uri).rstrip("&")
        uri += f'&index={"yes" if index else "no"}'
        uri.replace("?&", "?")

        feat = QgsFeature()
        feat.setGeometry(geom)

        if columns:
            feat.initAttributes(len(columns))

            if False:
                for field_idx, attr in enumerate(columns.values()):
                    feat.setAttribute(field_idx, attr)
            else:
                feat.setAttributes(
                    list(to_string_if_not_of_exact_type(columns.values()))
                )

        layer = QgsVectorLayer(uri, layer_name, "memory")
        layer_data_provider = (
            layer.dataProvider()
        )  # DEFAULT DATA PROVIDER, TODO: MAYBE CHANGE THIS
        assert feat.isValid(), f"{feat} was invalid"
        res, out_feats = layer_data_provider.addFeatures([feat])

        if not res:
            _logger.error(f"{layer_data_provider.lastError()}")

            assert (
                res
            ), f"Failure while adding features {res} {layer_data_provider.lastError()}"

        layer_data_provider.updateExtents()

        if SKIP_MEMORY_LAYER_CHECK_AT_CLOSE:
            layer.setCustomProperty("skipMemoryLayersCheck", 1)

        if categorise_by_attribute:
            categorise_layer(
                layer,
                categorise_by_attribute,
                color_iterable=color_generator,
                opacity=opacity,
            )

        layer.commitChanges()
        layer.updateFields()
        layer.updateExtents()

        return_collection.append(layer)

        if group:
            qgis_project.addMapLayer(layer, False)
            group.insertLayer(0, layer)
        else:
            qgis_project.addMapLayer(layer)

        layer_tree_handle = qgis_project.layerTreeRoot().findLayer(layer.id())
        if layer_tree_handle:
            layer_tree_handle.setItemVisibilityChecked(visible)

    actions = qgis.utils.iface.layerTreeView().defaultActions()
    actions.showFeatureCount()
    actions.showFeatureCount()  # TODO: Duplicate?

    return return_collection


@passes_kws_to(add_qgis_single_feature_layer)
def add_qgis_single_geometry_layers(
    qgis_instance_handle: Any, geoms: Mapping, **kwargs  # [str,QgsGeometry]
) -> None:
    """

    :param qgis_instance_handle:
    :param geoms:
    :param kwargs:
    :return:
    """
    for name, geom in geoms.items():
        add_qgis_single_feature_layer(qgis_instance_handle, geom, name, **kwargs)


def add_qgis_multi_feature_layer(
    qgis_instance_handle: Any,
    geoms: Iterable,  # [QgsGeometry]
    name: Optional[Iterable[str]] = None,
    crs: Optional[str] = None,
    columns: Optional[
        Union[Mapping[str, Mapping[str, Any]], Iterable[Mapping[str, Any]]]
    ] = None,
    categorise_by_attribute: Optional[str] = None,
    color_generator: Iterable = n_uint_mix_generator_builder(
        255, 255, 255, mix_min=(222, 222, 222)
    ),
    index: bool = False,
    group: Any = None,
    visible: bool = True,
    opacity: float = 1.0,
    measurements: Optional[Iterable[Iterable[float]]] = None,
) -> Optional[List]:
    """

        fields  == column definition name, type, length/size
        Multiple field parameters can be added to the data provider definition. type is one of “integer”,
        “double”, “string”.

    An example url is “Point?crs=epsg:4326&field=id:integer&field=name:string(20)&index=yes”

    :param measurements: UNUSED!
    :param opacity:
    :param color_generator:
    :param categorise_by_attribute:
    :param visible:
    :param group:
    :param qgis_instance_handle:
    :param geoms:
    :param name:
    :param crs:
    :param columns:
    :param index:
    :return:
    """

    from jord.qgis_utilities.categorisation import categorise_layer

    # noinspection PyUnresolvedReferences
    from qgis.core import (
        QgsFeature,
        QgsVectorLayer,
        QgsProject,
        QgsFeatureSink,
        QgsWkbTypes,
    )

    # noinspection PyUnresolvedReferences
    import qgis

    # uri = geom.type()
    # uri = geom.wkbType()
    # uri = geom.wktTypeStr()

    return_collection = []

    if name is None:
        name = DEFAULT_LAYER_NAME

    if crs is None:
        crs = DEFAULT_LAYER_CRS

    layer_name = f"{name}"
    if APPEND_TIMESTAMP:
        layer_name += f"_{time.time()}"

    geom_type = None
    uri = None

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

    if categorise_by_attribute and fields:
        assert (
            categorise_by_attribute in fields
        ), f"{categorise_by_attribute} was not found in {fields}"

    if not geoms:
        # logger.info(f"Found no geometries, {geoms} for {name}")
        return  # No geometry

    features = []
    if not isinstance(geoms, Iterable):
        geoms = [geoms]

    for geom in geoms:
        # geom:QgsGeometry

        if geom.wkbType() == QgsWkbTypes.NoGeometry:
            continue

        geom_type_ = QgsWkbTypes.displayString(geom.wkbType())

        if geom_type is None:
            geom_type = geom_type_

        if uri is None:
            uri = geom_type_  # TODO: URI MIGHT BE NONE?

        assert (
            geom_type == geom_type_
        ), f"{geom_type_} is the not the same geometry type as {geom_type}"

        if geom_type in (  # TODO: VERIFY LOGIC!
            QgsWkbTypes.GeometryCollection,
            QgsWkbTypes.GeometryCollectionZ,
            QgsWkbTypes.GeometryCollectionM,
            QgsWkbTypes.GeometryCollectionZM,
        ):
            for g in geom.asGeometryCollection():  # TODO: Look into recursion?

                sub_type = QgsWkbTypes.displayString(g.wkbType())

                return_collection.extend(
                    add_qgis_multi_feature_layer(
                        qgis_instance_handle,
                        g,
                        f"{name}_{sub_type}",
                        crs=crs,
                        columns=columns,
                        categorise_by_attribute=categorise_by_attribute,
                        color_generator=color_generator,
                        index=index,
                        group=group,
                        visible=visible,
                        opacity=opacity,
                        measurements=measurements,  # TODO: THIS WILL BE WEIRD!
                    )
                )
            return return_collection
        else:
            feat = QgsFeature()

            if attr_generator:
                row = next(attr_generator, None)
                if row:
                    feat.initAttributes(num_cols)
                    feat.setAttributes(
                        list(to_string_if_not_of_exact_type(row.values()))
                    )

            feat.setGeometry(geom)

            assert feat.isValid(), f"{feat} was invalid"
            features.append(feat)

    if STRICT:
        assert len(list(geoms)) == len(
            features
        ), f"Some features where dropped! {len(list(geoms))} != {len(features)}"
    else:
        if len(list(geoms)) != len(features):
            _logger.error(
                f"Some features where dropped! {len(list(geoms))} != {len(features)}"
            )

    if uri is None:
        if STRICT:
            raise Exception("uri is None")
        else:
            return return_collection

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

        if not res:
            msg = (
                f"Failure while adding features {res} {layer_data_provider.lastError()}"
            )
            assert res, msg
            _logger.warning(msg)

        assert len(list(geoms)) == len(
            out_feats
        ), f"Some features where dropped! return status {res}:  {len(list(geoms))} != {len(out_feats)}"

    if len(list(geoms)) != layer.featureCount():
        _logger.error(f"{features}")

    if STRICT:
        assert (
            len(list(geoms)) == layer.featureCount()
        ), f"Some features where dropped! {len(list(geoms))} != {layer.featureCount()}"
    else:
        if len(list(geoms)) != layer.featureCount():
            _logger.error(
                f"Some features where dropped! {len(list(geoms))} != {layer.featureCount()}"
            )

    layer_data_provider.updateExtents()

    if SKIP_MEMORY_LAYER_CHECK_AT_CLOSE:
        layer.setCustomProperty("skipMemoryLayersCheck", 1)

    if categorise_by_attribute:
        categorise_layer(
            layer,
            categorise_by_attribute,
            color_iterable=color_generator,
            opacity=opacity,
        )

    if STRICT:
        assert (
            len(list(geoms)) == layer.featureCount()
        ), f"Some features where dropped! {len(list(geoms))} != {layer.featureCount()}"
    else:
        if len(list(geoms)) != layer.featureCount():
            _logger.error(
                f"Some features where dropped! {len(list(geoms))} != {layer.featureCount()}"
            )

    layer.commitChanges()
    layer.updateFields()
    layer.updateExtents()

    if STRICT:
        assert (
            len(list(geoms)) == layer.featureCount()
        ), f"Some features where dropped! {len(list(geoms))} != {layer.featureCount()}"
    else:
        if len(list(geoms)) != layer.featureCount():
            _logger.error(
                f"Some features where dropped! {len(list(geoms))} != {layer.featureCount()}"
            )

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
