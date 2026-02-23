import numpy
from geopandas import GeoDataFrame, GeoSeries
from pandas import DataFrame

from jord.qlive_utilities import build_package
from jord.qlive_utilities.client import QliveClient
from jord.qlive_utilities.procedures import QliveRPCMethodEnum, QliveRPCMethodMap

build_package
numpy
QliveRPCMethodMap
QliveRPCMethodEnum

DEFAULT_CRS = "EPSG:3857"  # "EPSG:4326"
crs = DEFAULT_CRS

example_wkt_polygon = (
    "POLYGON((10.689697265625 -25.0927734375, 34.595947265625 "
    "-20.1708984375, 38.814697265625 -35.6396484375, 13.502197265625 "
    "-39.1552734375, 10.689697265625 -25.0927734375))"
)

example_wkt_gm = (
    "GEOMETRYCOLLECTION(POINT(0 0), LINESTRING(0 0, 1440 900), POLYGON((0 0, 0 1024, 1024 1024, "
    "1024 0, 0 0)))"
)

with QliveClient("tcp://localhost:5555") as qlive:
    if False:
        image = Image.open("exclude/mp.png")  # "exclude/duck_bat.jpg")
        if True:
            gray_scale = image.convert("L")
            raster_ = numpy.asarray(gray_scale)
        else:
            raster_ = numpy.asarray(image)

        raster_ = raster_.astype(numpy.uint8)

        if False:
            print(raster_.shape)
            pyplot.imshow(raster_, cmap="gray")
            pyplot.show()
        else:
            print(
                qlive.send(
                    build_package(
                        QliveRPCMethodEnum.add_raster,
                        raster_,
                        "mp_raster",
                        None,
                        None,
                        1,  # 0.01,
                        "EPSG:4326",
                    )
                )
            )

    if False:
        qlive.send(
            build_package(
                QliveRPCMethodEnum.add_wkts,
                {"gm1": example_wkt_gm, "poly1": example_wkt_polygon},
            )
        )

    if True:
        df = DataFrame(
            {
                "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
                "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
                "layer": ["layer1", "layer2", "layer3", "layer4", "layer5"],
                "Coordinates": [
                    "POINT(-58.66 -34.58)",
                    "POINT(-47.91 -15.78)",
                    "POINT(-70.66 -33.45)",
                    "POINT(-74.08 4.60)",
                    "POINT(-66.86 10.48)",
                ],
            }
        )

        df["Coordinates"] = GeoSeries.from_wkt(df["Coordinates"])
        data_frame = GeoDataFrame(df, geometry="Coordinates")

        if False:
            qlive.send(
                build_package(
                    QliveRPCMethodEnum.add_dataframe,
                    data_frame,
                )
            )
        else:
            qlive.add_dataframe(data_frame)
