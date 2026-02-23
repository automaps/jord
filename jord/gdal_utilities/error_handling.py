from enum import Enum

from jord.gdal_utilities import GDAL

__all__ = ["gdal_error_type_map", "GdalErrorTypeEnum", "gdal_error_handler"]


class GdalErrorTypeEnum(Enum):
    none = GDAL.CE_None
    debug = GDAL.CE_Debug
    warning = GDAL.CE_Warning
    failure = GDAL.CE_Failure
    fatal = GDAL.CE_Fatal


gdal_error_type_map = {v.value: str(v.name).capitalize() for v in GdalErrorTypeEnum}


def gdal_error_handler(err_class, err_num, err_msg) -> None:
    """

    :param err_class:
    :type err_class:
    :param err_num:
    :type err_num:
    :param err_msg:
    :type err_msg:
    """
    err_msg = err_msg.replace("\n", " ")
    err_class = gdal_error_type_map.get(err_class, "None")
    print(f"Error Number: {err_num}")
    print(f"Error Type: {err_class}")
    print(f"Error Message: {err_msg}")


if __name__ == "__main__":
    print(gdal_error_type_map)
    ...
    # GDAL.PushErrorHandler(gdal_error_handler)
