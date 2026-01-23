from pathlib import Path

from ezdxf.addons import odafc
from typing import Optional

__doc__ = r"""

from ezdxf.addons import odafc

# Load a DWG file
doc = odafc.readfile('my.dwg')

# Use loaded document like any other ezdxf document
print(f'Document loaded as DXF version: {doc.dxfversion}.')
msp = doc.modelspace()
...

# Export document as DWG file for AutoCAD R2018
odafc.export_dwg(doc, 'my_R2018.dwg', version='R2018')



ezdxf.addons.odafc.win_exec_path = "C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"


ezdxf.addons.odafc.unix_exec_path = "ODAFileConverter"

https://ezdxf.readthedocs.io/en/stable/addons/odafc.html
"""

__all__ = ["convert_to_dxf"]


def convert_to_dxf(
    dwg_file_path: Path,
    oda_converter_path: Optional[
        Path
    ] = r"C:\Program Files\ODA\ODAFileConverter 25.4.0\ODAFileConverter.exe",
    target_dir: Optional[Path] = None,
) -> Path:
    # Load a DWG file
    # doc = odafc.readfile('my.dwg')

    # Use loaded document like any other ezdxf document
    # print(f'Document loaded as DXF version: {doc.dxfversion}.')
    # msp = doc.modelspace()
    # ...

    # Export document as DWG file for AutoCAD R2018
    # odafc.export_dwg(doc, 'my_R2018.dwg', version='R2018')

    if oda_converter_path:
        if not isinstance(oda_converter_path, Path):
            oda_converter_path = Path(oda_converter_path)

        odafc.win_exec_path = str(oda_converter_path)

    if not isinstance(dwg_file_path, Path):
        dwg_file_path = Path(dwg_file_path)

    if target_dir:
        if not isinstance(target_dir, Path):
            target_dir = Path(target_dir)

        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)

        dxf_file_path = target_dir / dwg_file_path.name
    else:
        dxf_file_path = dwg_file_path.with_suffix(".dxf")

    odafc.convert(str(dwg_file_path), str(dxf_file_path), replace=True)

    return dxf_file_path


if __name__ == "__main__":

    def asdijai():
        win_path = Path(odafc.win_exec_path)
        print(win_path, win_path.exists())

        print(
            convert_to_dxf(
                Path(r"C:\Users\chen\Downloads\simple-christmas-objects.dwg")
            )
        )

    asdijai()
