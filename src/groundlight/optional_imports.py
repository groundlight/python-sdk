"""We use a trick to check if libraries like numpy are installed or not.
If they are, we make it available as normal.
If not, we set it up as a shim object which still lets type-hinting work properly,
but will fail at runtime if you try to use it.

This can be confusing, but hopefully the errors are explicit enough to be 
clear about what's happening, and it makes the code which hopes numpy is installed
look readable.
"""


class UnavailableModule(object):
    """Represents a module that is not installed or otherwise unavailable at runtime.
    Attempting to access anything in this object raises the original exception
    (ImportError or similar) which happened when the optional library failed to import.
    """

    def __init__(self, exc: Exception):
        self.exc = exc

    def __getattr__(self, key):
        raise RuntimeError("attempt to use module that failed to load") from self.exc


try:
    import numpy as np
except ImportError as e:
    np = UnavailableModule(e)
    # Expose np.ndarray so type-hinting looks normal
    np.ndarray = np

try:
    import PIL

    Image = PIL.Image
except ImportError as e:
    PIL = UnavailableModule(e)
    Image = PIL


__all__ = ["np", "PIL", "Image"]
