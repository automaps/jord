from pathlib import Path

import pandas
import shapely
from enum import Enum
from pandas import DataFrame
from shapely import wkt
from typing import Any, Generator, Sequence

__all__ = ["load_wkts_from_csv", "csv_wkt_generator", "WktTypeEnum"]


class WktTypeEnum(Enum):
    (
        point,
        multipoint,
        linestring,
        multilinestring,
        polygon,
        multipolygon,
        geometrycollection,
    ) = (
        "point",
        "multipoint",
        "linestring",
        "multilinestring",
        "polygon",
        "multipolygon",
        "geometrycollection",
    )  # assigned_names()


def load_wkts_from_csv(
    csv_file_path: Path, geometry_column: str = "Shape", additional_cols: Sequence = ()
) -> DataFrame:
    """
    Well-Known Text
    """
    df = pandas.read_csv(
        str(csv_file_path), usecols=[*additional_cols, geometry_column]
    )
    df[geometry_column] = df[geometry_column].apply(wkt.loads)
    return df


def csv_wkt_generator(
    csv_file_path: Path, geometry_column: str = "Shape"
) -> Generator[shapely.geometry.base.BaseGeometry, Any, None]:
    """

    :param csv_file_path:
    :param geometry_column:
    :return:
    """
    for idx, g in pandas.read_csv(
        str(csv_file_path), usecols=[geometry_column]
    ).iterrows():
        yield wkt.loads(g)  # g is a pandas Series?


if __name__ == "__main__":

    def uashdu():
        for t in WktTypeEnum:
            print(t)

    uashdu()
