from jord.qlive_utilities.client import QliveClient

__all__ = ["InterfacedQliveClient"]


class InterfacedQliveClient(QliveClient):
    """
    Useful for making client-side validation of data
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def raster(self):
        """ """
        ...

    def geometry(self):
        """ """
        ...
