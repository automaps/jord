import numpy
from enum import Enum

# noinspection PyUnresolvedReferences
from qgis.core import Qgis
from typing import Any


class QgisDataTypeEnum(Enum):
    unknown = Qgis.UnknownDataType  # Unknown or unspecified type.

    # int8 = Qgis.Int8  # Eight bit signed integer (qint8) (added in QGIS 3.30)
    int16 = Qgis.Int16  # Sixteen bit signed integer (qint16)
    int32 = Qgis.Int32  # Thirty two bit signed integer (qint32)

    uint8 = Qgis.Byte  # Eight bit unsigned integer (quint8)
    uint16 = Qgis.UInt16  # Sixteen bit unsigned integer (quint16)
    uint32 = Qgis.UInt32  # Thirty two bit unsigned integer (quint32)

    float32 = Qgis.Float32  # Thirty two bit floating point (float)
    float64 = Qgis.Float64  # Sixty four bit floating point (double)

    cint16 = Qgis.CInt16  # Complex Int16.
    cint32 = Qgis.CInt32  # Complex Int32.

    cfloat32 = Qgis.CFloat32  # Complex Float32.
    cfloat64 = Qgis.CFloat64  # Complex Float64.

    argb32 = (
        Qgis.ARGB32
    )  # Color, alpha, red, green, blue, 4 bytes the same as QImage::Format_ARGB32.
    argb32pre = (
        Qgis.ARGB32_Premultiplied
    )  # Color, alpha, red, green, blue, 4 bytes the same as QImage::Format_ARGB32_Premultiplied.


NUMPY_TO_QGIS_TYPE_MAPPING = {  # Numpy type         C type      Description
    numpy.bool_: QgisDataTypeEnum.uint8,  # bool Boolean (True or False) stored as a byte
    numpy.int_: QgisDataTypeEnum.int32,  # long Platform-defined
    numpy.complex_: QgisDataTypeEnum.unknown,
    numpy.float_: QgisDataTypeEnum.unknown,
    # numpy.byte: QgisDataTypeEnum.int8,  # signed char Platform-defined
    numpy.ubyte: QgisDataTypeEnum.uint8,  # unsigned char Platform-defined
    # numpy.short: QgisDataTypeEnum.int8,  # short Platform-defined
    numpy.intc: QgisDataTypeEnum.cint16,  # int Platform-defined
    # numpy.int8: QgisDataTypeEnum.int8,
    numpy.intp: QgisDataTypeEnum.unknown,
    numpy.int16: QgisDataTypeEnum.int16,
    numpy.int32: QgisDataTypeEnum.int32,
    numpy.int64: QgisDataTypeEnum.unknown,
    numpy.longlong: QgisDataTypeEnum.unknown,  # long long Platform-defined
    numpy.ushort: QgisDataTypeEnum.uint8,  # unsigned short Platform-defined
    numpy.uintc: QgisDataTypeEnum.unknown,  # unsigned int Platform-defined
    numpy.uint: QgisDataTypeEnum.uint32,  # unsigned long Platform-defined
    numpy.uint8: QgisDataTypeEnum.uint8,
    numpy.uint16: QgisDataTypeEnum.uint16,
    numpy.uint32: QgisDataTypeEnum.uint32,
    numpy.uint64: QgisDataTypeEnum.unknown,
    numpy.ulonglong: QgisDataTypeEnum.unknown,  # unsigned long long Platform-defined
    numpy.half: QgisDataTypeEnum.unknown,  # Half precision float: sign bit, 5 bits exponent, 10 bits mantissa
    numpy.float16: QgisDataTypeEnum.unknown,
    # Half precision float: sign bit, 5 bits exponent, 10 bits mantissa
    numpy.float32: QgisDataTypeEnum.float32,
    numpy.float64: QgisDataTypeEnum.float64,
    numpy.single: QgisDataTypeEnum.float32,
    # float Platform-defined single precision float: typically sign bit,
    # 8 bits exponent,  # 23 bits mantissa
    numpy.double: QgisDataTypeEnum.float64,
    # double Platform-defined double precision float: typically sign bit,
    # 11 bits exponent, 52 bits mantissa.
    numpy.longdouble: QgisDataTypeEnum.unknown,  # long double Platform-defined extended-precision float
    numpy.csingle: QgisDataTypeEnum.cfloat32,
    # float complex Complex number, represented by two single-precision
    # floats (
    # real and imaginary components)
    numpy.cdouble: QgisDataTypeEnum.cfloat64,
    # double complex Complex number, represented by two double-precision
    # floats (
    # real and imaginary
    # components).
    numpy.clongdouble: QgisDataTypeEnum.unknown,
    # long double complex  # Complex number, represented by two extended-precision floats (real and
    # imaginary components).
    numpy.complex64: QgisDataTypeEnum.unknown,
    numpy.complex128: QgisDataTypeEnum.unknown,
}


def get_qgis_type(dtype: numpy.dtype) -> Any:
    """

    :param dtype:
    :return:
    """
    return NUMPY_TO_QGIS_TYPE_MAPPING[dtype.type]
