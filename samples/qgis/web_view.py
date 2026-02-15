__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

from PyQt5.QtWebKitWidgets import QWebView


from qgis.PyQt.QtCore import (
    QUrl,
)
from typing import Any


def get_web_view(parent: Any) -> QWebView:
    my_web_view = QWebView(parent)
    # self.my_web_page = QWebPage()
    # self.my_web_page
    # self.my_web_view.setPage(self.my_web_page)
    # self.my_web_view.setUrl(QtCore.QUrl("http://www.google.com"))
    html_template = """
            <!DOCTYPE html>
            <html>
            <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
            <meta charset="utf-8">
            <title>Simple Polylines</title>
            <style>
            html, body {
                height: 100%;
                }
            #map {
                height: 100%;
                }
            </style>
            </head>
            <body>
            <div id="map"></div>
            </body>
            <script>
            function initMap() {}
            </script>
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD-9tCzsZ0-ZgK_ZgXZ-_XzQ_XzQ_XzQ_X
            &callback=initMap"
            async defer></script>
            </html>
            """

    # self.my_web_view.loadHtml(self.html_template)
    url = "https://qgis.org"
    my_web_view.load(QUrl(url))
    return my_web_view
