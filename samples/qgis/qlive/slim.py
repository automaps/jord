import numpy
import zmq

from jord.qlive_utilities.procedures import QliveRPCMethodEnum
from jord.qlive_utilities.serialisation import build_package

context = zmq.Context()

socket = context.socket(zmq.REQ)

socket.connect("tcp://localhost:5555")

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

if False:
    socket.send(build_package(QliveRPCMethodEnum.add_wkt, example_wkt_polygon))
    print("sent")
    message = socket.recv()
    print(message)

if False:
    socket.send(build_package(QliveRPCMethodEnum.add_wkt, example_wkt_gm))
    print("sent")
    message = socket.recv()
    print(message)

if True:
    from PIL import Image

    image = Image.open("exclude/duck_bat.jpg")
    gray_scale = image.convert("L")
    raster_ = numpy.asarray(gray_scale)
    print(raster_.shape)

    if False:
        pyplot.imshow(raster_, cmap="gray")
        pyplot.show()
    else:
        socket.send(build_package(QliveRPCMethodEnum.add_raster, raster_, "duck_bat"))
        print("sent")
        message = socket.recv()
        print(message)

if False:
    socket.send(
        build_package(
            QliveRPCMethodEnum.add_wkts,
            {"gm1": example_wkt_gm, "poly1": example_wkt_polygon},
        )
    )
    print("sent")
    message = socket.recv()
    print(message)
