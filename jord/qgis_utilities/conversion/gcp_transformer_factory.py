from pathlib import Path

from qgis.analysis import QgsGcpGeometryTransformer, QgsGcpTransformerInterface
from qgis.core import QgsPointXY

__all__ = ["get_gcp_transformer_from_file"]

from .read_gcp_read import read_gcp_file


def get_gcp_transformer_from_file(
    gcp_points_file_path: Path,
    method: QgsGcpTransformerInterface = QgsGcpTransformerInterface.TransformMethod.Helmert,
    *,
    filter_comments: bool = True
) -> QgsGcpGeometryTransformer:
    """

    :param gcp_points_file_path:
    :type gcp_points_file_path:
    :param method:
    :type method:
    :param filter_comments:
    :type filter_comments:
    :return:
    :rtype:
    """
    source_xy, dest_xy = read_gcp_file(
        gcp_points_file_path, filter_comments=filter_comments
    )

    assert (len(source_xy) == len(dest_xy)) and len(
        source_xy
    ) >= QgsGcpTransformerInterface.create(
        QgsGcpTransformerInterface.TransformMethod(method)
    ).minimumGcpCount()

    return QgsGcpGeometryTransformer(
        method, (QgsPointXY(*s) for s in source_xy), (QgsPointXY(*d) for d in dest_xy)
    )
