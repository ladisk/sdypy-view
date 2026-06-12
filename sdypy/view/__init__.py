from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sdypy-view")
except PackageNotFoundError:  # source checkout without installed metadata
    __version__ = "0+unknown"

from .pyvista_3D import *