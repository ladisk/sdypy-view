from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sdypy-view")
except PackageNotFoundError:  # source checkout without installed metadata
    __version__ = "0+unknown"

from .pyvista_3D import Plotter3D, create_fem_mesh, prepare_animation_displacements, prepare_animation_field, copy_image_to_clipboard

__all__ = ["Plotter3D", "create_fem_mesh", "prepare_animation_displacements", "prepare_animation_field", "copy_image_to_clipboard"]
