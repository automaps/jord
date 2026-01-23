import pandas
from pandas import DataFrame
from typing import Any, Collection, List, Mapping, Optional

__all__ = ["df_to_columns", "columns_to_df", "normalize_na"]


def df_to_columns(
    shape_df: DataFrame, ignored_columns: Optional[Collection] = None
) -> List[Mapping[str, Any]]:
    columns = []

    for key, c in shape_df.iterrows():
        o = {"key": key, **dict(c)}

        if ignored_columns:
            for p in ignored_columns:
                o.pop(p)

        columns.append(o)

    return columns


def columns_to_df(columns: List[Mapping[str, Any]]) -> DataFrame: ...


def normalize_na(d: Any) -> Optional[str]:
    if pandas.isna(d):
        return None

    # If needed, implement proper display rule normalization logic here
    # This could involve parsing the string representation and ensuring
    # extrusion is either None or properly initialized

    return str(d)
