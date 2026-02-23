__all__ = ["load_spatialite"]

import sqlite3


def load_spatialite(dbapi_conn: sqlite3.Connection, *args, **kwargs) -> None:
    """

    :param dbapi_conn:
    :type dbapi_conn:
    :param args:
    :type args:
    :param kwargs:
    :type kwargs:
    """
    dbapi_conn.enable_load_extension(True)
    dbapi_conn.load_extension("mod_spatialite")
