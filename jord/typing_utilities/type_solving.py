import datetime
import logging
import numpy
import pandas
import shapely
from pandas.core.generic import NDFrame
from typing import (
    Any,
    Collection,
    Generator,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

ADD_STRING_LEN = True
NUM_MB16_CHARS = 16777216

__all__ = [
    "solve_qgis_type",
    "solve_type_configuration",
    "solve_attribute_uri",
    "solve_field_uri",
    "to_string_if_not_of_exact_type",
    "to_truth",
]

_logger = logging.getLogger(__name__)


def solve_qgis_type(
    d: Any, floating_point_length: int = 20, floating_point_precision: int = 8
) -> Optional[str]:
    """
    Does not support size/length yet...

    QGIS Available Field types:
    ________________           - Provider type ( MemoryLayer) - implemented

    Whole Number (integer) - integer - X
    Decimal Number (real) - double - X
    Text (string) - string - X
    Date - date - X
    Time - time - X
    Date & Time - datetime - X
    Whole Number ( ... llint - 16bit) - int2 - O
    Whole Number (integer - 32bit) - int4 - O
    Whole Number (integer - 64bit) - int8 - O
    Decimal Number (numeric) - numeric - O
    Decimal Number (decimal) - decimal - O
    Decimal Number (real) - real - O
    Decimal Number (double) - double precision - O
    Text, unlimited length (text) - text - X
    Boolean - boolean  - X
    Binary Object (BLOB) - binary - X
    String List - stringlist - X
    Integer List - integerlist - O
    Decimal (double) List - doublelist - O
    Integer (64 bit) List - integer64list - O
    Map - map - O
    Geometry - geometry - O

    :param floating_point_precision:
    :param floating_point_length:
    :param d:
    :return:
    """
    if d is None:
        return None

    if not isinstance(d, bool):
        if isinstance(d, int):
            return "integer"

        elif isinstance(d, float):  # and (math.isnan(d)):
            return f"double"  # ({floating_point_length,floating_point_precision})" #'real' #"double"

        elif isinstance(d, bytes):
            return "binary"

        elif isinstance(d, (list, tuple, set)):  # ASSUME IS STRINGS
            return "stringlist"

        elif isinstance(
            d,
            (
                datetime.datetime
                #    , pandas.NaT
            ),
        ):
            return "datetime"

        elif isinstance(d, datetime.date):
            return "date"

        elif isinstance(d, datetime.time):
            return "time"

        elif isinstance(d, shapely.Polygon):
            return "geometry"  # "polygon"

        elif isinstance(d, shapely.MultiPolygon):
            return "geometry"  # "multipolygon"

        elif isinstance(d, shapely.LineString):
            return "geometry"  # "linestring"

        elif isinstance(d, shapely.MultiLineString):
            return "geometry"  # "multilinestring"

        elif isinstance(d, shapely.MultiPoint):
            return "geometry"  # "multipoint"

        elif isinstance(d, shapely.Point):
            return "geometry"  # "point"

        elif isinstance(d, str):
            if False:
                if (
                    ADD_STRING_LEN
                ):  # WARNING! Shapefiles have a limitation of maximum 254 characters per field
                    return f"string({min(max(len(d) * 16, 255), NUM_MB16_CHARS)})"  # 16x buffer for large strings
            else:
                return "text"
        else:
            if False:
                _logger.error(
                    f"Could not solve type {type(d)=}, {d.__class__.__name__}"
                )
    try:
        if to_truth(numpy.isnan(d)):
            return None
    except:
        ...

    try:
        if isinstance(d, NDFrame) and d.size == 0:
            return None
    except:
        ...

    try:
        if to_truth(pandas.isna(d)):
            return None
    except:
        ...

    if isinstance(d, bool):
        if False:
            if ADD_STRING_LEN:
                return "string(255)"  # True, False (5)
        else:
            if False:
                _logger.error(f"Fallback solve type {type(d)=}, {d.__class__.__name__}")
            return "boolean"

    if False:
        return "text"

    return "string"


def solve_attribute_uri(
    attr_type_sampler: Generator,
    columns: Collection,
    floating_point_length: int = 20,
    floating_point_precision: int = 8,
) -> Tuple[Mapping[str, str], Mapping[str, str], int]:

    sample_row = next(attr_type_sampler)
    num_cols = len(sample_row)

    fields = {}
    field_type_configuration = {}
    for data_key, data_value in sample_row.items():
        data_type = solve_qgis_type(data_value)

        if fields.get(data_key) is None:
            fields[data_key] = data_type

        if data_type:
            if field_type_configuration.get(data_key) is None:
                field_type_configuration[data_key] = solve_type_configuration(
                    data_value, data_key, columns
                )

    for row in attr_type_sampler:
        _solved = True
        for data_key in fields.keys():
            if fields.get(data_key) is None:
                _solved = False

        if _solved:
            break

        for data_key, data_value in row.items():
            data_type = solve_qgis_type(data_value)

            if fields.get(data_key) is None:
                fields[data_key] = data_type

            if data_type:
                if field_type_configuration.get(data_key) is None:
                    field_type_configuration[data_key] = solve_type_configuration(
                        data_value, data_key, columns
                    )

    for f in list(fields.keys()):
        if f not in field_type_configuration:
            field_type_configuration[f] = None

    return field_type_configuration, fields, num_cols


def solve_field_uri(
    field_type_configuration: Mapping, fields: Mapping, uri: str
) -> str:
    uri = str(uri).rstrip("&")

    for k, v in fields.items():
        uri += f"&field={k}:{v}"
        if field_type_configuration is not None and k in field_type_configuration:
            c = field_type_configuration[k]
            if c:
                uri += f"({c})"

    return uri


def to_string_if_not_of_exact_type(
    gen: Iterable, type_: Iterable[type] = (int, float, str, bool, datetime.datetime)
) -> Union[str, Any]:
    """

    :param type_: Type for testing against
    :param gen: The iterable to be converted
    :return:
    """
    if not isinstance(type_, Iterable):
        type_ = [type_]

    for v in gen:
        if v is None:
            yield None
        elif isinstance(v, Collection):
            if False:
                yield list(
                    str(v_) if all([type(v_) != t for t in type_]) else v_ for v_ in v
                )  # TODO: SHOULD ALSO BE CONVERTED?
            else:
                yield v
        elif pandas.isna(v):
            yield None
        elif isinstance(v, datetime.datetime):

            yield v.isoformat()  # pandas.to_datetime(v)

        elif all([type(v) != t for t in type_]):  # UNKNOWN TYPE
            s = str(v)
            if False and len(s.strip()) == 0:
                yield None
            else:
                yield s
        else:
            yield v


def solve_type_configuration(
    data_value: Any,
    data_key: Optional[str],
    columns: Optional[List],
    allocation_multiplier: Optional[int] = 2,
    floating_point_length: int = 20,
    floating_point_precision: int = 8,
) -> Optional[str]:
    """

      :param floating_point_length:
    :param floating_point_precision:
    :param data_value:
    :param data_key:
    :param columns:
    :param allocation_multiplier:
    :return:
    """
    if isinstance(data_value, float):
        return f"{floating_point_length},{floating_point_precision}"

    if isinstance(data_value, str):
        a = len(data_value)

        if data_key and columns:
            max_len = a

            if isinstance(columns, Iterable):
                for cols in columns:
                    c = cols[data_key]

                    if isinstance(c, str):
                        max_len = max(max_len, len(c))

            a = max_len

        if allocation_multiplier:
            a *= allocation_multiplier

        a = max(a, 255)
        return str(a)

    return None


def to_truth(a: Any) -> bool:
    if isinstance(a, Iterable):

        try:
            if isinstance(a, numpy.ndarray):
                return a.all()
        except:
            ...
        return all(a)

    return a
