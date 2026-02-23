__all__ = ["plugin_status"]


def plugin_status(plugin_key: str) -> str:
    """

    :param plugin_key:
    :type plugin_key:
    :return:
    :rtype:
    """
    from pyplugin_installer.installer_data import plugins  # QGIS CODE!

    all_plugins = plugins.all()

    if plugin_key in all_plugins:
        return all_plugins[plugin_key]["status"]

    return "Not Found"


# utils.reloadPlugin()
