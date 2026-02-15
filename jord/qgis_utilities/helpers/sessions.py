from qgis.core import QgsMapLayer, QgsRasterDataProvider
from warg import AlsoDecorator

__all__ = ["QLayerEditSession", "RasterDataProviderEditSession"]


class QLayerEditSession(AlsoDecorator):

    def __init__(self, map_layer: QgsMapLayer):
        self.map_layer = map_layer

    def __enter__(self):
        if self.map_layer:
            self.map_layer.startEditing()
        return True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.map_layer:
            self.map_layer.commitChanges()


class RasterDataProviderEditSession(AlsoDecorator):

    def __init__(
        self, raster_data_provider: QgsRasterDataProvider, auto_reload: bool = True
    ):
        self.raster_data_provider = raster_data_provider
        self.auto_reload = auto_reload

    def __enter__(self):
        if self.raster_data_provider:
            self.raster_data_provider.setEditable(True)
        return True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.raster_data_provider:
            self.raster_data_provider.setEditable(False)
            if self.auto_reload:
                self.raster_data_provider.reload()
