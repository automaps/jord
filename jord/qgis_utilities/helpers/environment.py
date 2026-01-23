__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

from pathlib import Path

import os
import subprocess
import sys
from subprocess import check_output
from typing import Iterable, Optional, Tuple

__all__ = ["install_requirements_from_file", "install_requirements_from_name"]

SP_CALLABLE = subprocess.check_call  # subprocess.call


def install_requirements_from_file(requirements_path: Path) -> None:
    """
    Install requirements from a requirements.txt file.

    :param requirements_path: Path to requirements.txt file.

    """

    # pip.main(["install", "pip", "--upgrade"]) # REQUIRES RESTART OF QGIS

    args = ["install", "-r", str(requirements_path), "--upgrade"]
    # args = ["install", "rasterio", "--upgrade"] # RASTERIO for window DOES NOT WORK ATM, should be installed
    # manually

    if False:
        import pip

        pip.main(args)

    elif False:
        SP_CALLABLE(["pip"] + args)

    elif True:
        SP_CALLABLE(["python", "-m", "pip"] + args)


def is_requirement_installed(requirement_name: str) -> bool:
    if requirement_has_version(requirement_name):
        if get_requirement_version(requirement_name) == get_installed_version(
            requirement_name
        ):
            return True
    if get_installed_version(requirement_name):
        return True
    return False


def requirement_has_version(requirement_name: str) -> bool:
    return get_requirement_version(requirement_name) is not None


def get_requirement_version(requirement_name: str) -> Optional[str]:
    s = requirement_name.split("==")
    if len(s) == 2:
        return s[-1]
    return None


def get_installed_version(requirement_name: str) -> Optional[str]:
    import pkg_resources

    try:
        dist = pkg_resources.get_distribution(requirement_name)
        if dist:
            return dist.parsed_version  # .version
    except pkg_resources.DistributionNotFound as e:
        pass
    return None


def get_newest_version(
    requirement_name: str,
    pip_index=os.environ.get("PIP_INDEX_URL", "https://pypi.org/pypi/"),
) -> str:
    """

    :param requirement_name:
    :param pip_index:
    :return:
    """
    from pkg_resources import parse_version

    import json
    from urllib.request import Request, urlopen

    def get_charset(headers, default: str = "utf-8"):
        # this is annoying.
        try:
            charset = headers.get_content_charset(default)
        except AttributeError:
            # Python 2
            charset = headers.getparam("charset")
            if charset is None:
                ct_header = headers.getheader("Content-Type")
                import cgi

                content_type, params = cgi.parse_header(ct_header)
                charset = params.get("charset", default)
        return charset

    def json_get(url: str, headers: Tuple = (("Accept", "application/json"),)):
        request = Request(url=url, headers=dict(headers))
        response = urlopen(request)
        code = response.code
        if code != 200:
            err = ConnectionError(f"Unexpected response code {code}")
            err.response_data = response.read()
            raise err
        raw_data = response.read()
        response_encoding = get_charset(response.headers)
        decoded_data = raw_data.decode(response_encoding)
        data = json.loads(decoded_data)
        return data

    def get_data_pypi(name: str, index: str = pip_index):
        uri = f"{index.rstrip('/')}/{name.split('[')[0]}/json"
        data = json_get(uri)
        return data

    def get_versions_pypi(name: str, index: str = pip_index):
        data = get_data_pypi(name, index)
        version_numbers = sorted(data["releases"], key=parse_version)
        return tuple(version_numbers)

    return parse_version(get_versions_pypi(requirement_name)[-1])


def is_requirement_updatable(requirement_name: str) -> bool:
    if not is_requirement_installed(requirement_name):
        return True

    if requirement_has_version(requirement_name):
        if get_requirement_version(requirement_name) != get_installed_version(
            requirement_name
        ):
            return True

    if get_newest_version(requirement_name) > get_installed_version(requirement_name):
        return True

    return False


def install_requirements_from_name(*requirements_name: Iterable[str]) -> None:
    """
    Install requirements from names.

    :param requirements_name: Name of requirements.
    """
    # pip.main(["install", "pip", "--upgrade"]) # REQUIRES RESTART OF QGIS

    # if isinstance(requirements_name, Iterable) and len(requirements_name)==1:
    # ... # handle wrong input format

    args = ["install", "-U", *requirements_name]
    # args = ["install", "rasterio", "--upgrade"] # RASTERIO for window DOES NOT WORK ATM, should be installed
    # manually

    if False:
        import pip

        pip.main(args)

    elif False:
        SP_CALLABLE(["pip"] + args)
    # subprocess.check_call([sys.executable, '-m', 'conda', 'install', '<packagename>'])
    elif True:
        interpreter = Path(sys.executable).absolute()
        SP_CALLABLE([str(interpreter), "-m", "pip"] + args)


def remove_requirements_from_name(
    *requirements_name: Iterable[str], num_repeat: int = 1
) -> None:
    """
    Multiple colliding versions may be installed at once, (conda, pip, ....)

    :param num_repeat:     Repeat arg let you choose how many times to try to uninstall the packages.
    :param requirements_name:
    :return:
    """

    args = ["uninstall", "-y", *requirements_name]

    for _ in range(num_repeat):
        if False:
            import pip

            pip.main(args)

        elif False:
            SP_CALLABLE(["pip"] + args)

        elif True:
            interpreter = Path(sys.executable).absolute()
            SP_CALLABLE(
                [str(interpreter), "-m", "pip"] + args
            )  # figure out which python!

            for r in requirements_name:  # assuming no name aliasing
                del requirements_name  # unload now deleted modules

            reqs = check_output([sys.executable, "-m", "pip", "freeze"])
            # installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
            # print(installed_packages)


if __name__ == "__main__":
    print(
        get_newest_version("warg"),
        get_installed_version("warg"),
        get_newest_version("warg") == get_installed_version("warg"),
    )

    install_requirements_from_name("that")
    remove_requirements_from_name("that")
