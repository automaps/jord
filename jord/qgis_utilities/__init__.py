__author__ = "heider"
__doc__ = r"""

            This module must remain clean and clear of additional external dependencies outside of qgis,
            and base requirements of jord.

           Created on 5/5/22
           """

from pathlib import Path

import logging

with open(Path(__file__).parent / "README.md") as this_init_file:
    __doc__ += this_init_file.read()

try:
    from .configuration import *
    from .conversion import *
    from .helpers import *  # import issues
    from .numpy_utilities import *
    from .categorisation import *
    from .constraints import *
    from .data_provider import *
    from .enums import *
    from .fields import *
    from .geo_interface_serialisation import *
    from .geometry_types import *
    from .importing import *
    from jord.qlive_utilities.layer_creation import *
    from jord.qlive_utilities.layer_serialisation import *
    from .plugin_version import *
    from .styles import *
    from .styling import *
    from .iteration import *
    from .compatability import *
    from .gui_utilities import *
except ImportError as ix:
    this_package_name = Path(__file__).parent.name
    logging.error(f"Make sure qgis module is available for {this_package_name}")
    raise ix
