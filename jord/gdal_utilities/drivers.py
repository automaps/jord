from typing import Dict

from jord.gdal_utilities import OGR

__all__ = ["available_driver_index_name_mapping"]


def available_driver_index_name_mapping() -> Dict[str, int]:
    """

    :return:
    :rtype:
    """
    driver_map = {}
    for i in range(OGR.GetDriverCount()):
        driver_name = OGR.GetDriver(i).GetName()
        assert driver_name not in driver_map
        driver_map[driver_name] = i

    return driver_map


if __name__ == "__main__":
    print(available_driver_index_name_mapping())
