# ruff: noqa: N804
"""We use a trick to check if libraries like numpy are installed or not.
If they are, we make it available as normal.
If not, we set it up as a shim object which still lets type-hinting work properly,
but will fail at runtime if you try to use it.

This can be confusing, but hopefully the errors are explicit enough to be
clear about what's happening, and it makes the code which hopes numpy is installed
look readable.
"""


class UnavailableModule(type):
    """Represents a module that is not installed or otherwise unavailable at runtime.
    Attempting to access anything in this object raises the original exception
    (ImportError or similar) which happened when the optional library failed to import.

    Needs to subclass type so that it works for type-hinting.
    """

    def __new__(cls, exc):
        out = type("UnavailableModule", (), {})
        out.exc = exc
        return out

    def __getattr__(self, key):  # pylint: disable=bad-mcs-method-argument
        # TODO: This isn't getting called for some reason.
        raise RuntimeError("attempt to use module that failed to load") from self.exc  # type: ignore


try:
    import numpy as np  # pyright: reportMissingImports=false

    MISSING_NUMPY = False
except ImportError as e:
    np = UnavailableModule(e)
    # Expose np.ndarray so type-hinting looks normal
    np.ndarray = np  # pylint: disable=attribute-defined-outside-init
    MISSING_NUMPY = True

try:
    import PIL
    from PIL import Image

    MISSING_PIL = False
except ImportError as e:
    PIL = UnavailableModule(e)
    Image = PIL
    Image.Image = PIL  # for type-hinting; pylint: disable=attribute-defined-outside-init
    MISSING_PIL = True


__all__ = ["np", "PIL", "Image", "MISSING_NUMPY", "MISSING_PIL"]
