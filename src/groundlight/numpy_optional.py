"""A shim that checks if numpy is installed and makes parts of it
available if it is, otherwise fails explicitly.
This can be confusing, but hopefully the errors are explicit enough to be 
clear about what's happening, and it makes the code which hopes numpy is installed
look readable.
"""

class UnavailableModule(object):
    def __init__(self, exc: Exception):
        self.exc = exc
    def __getattr__(self, key):
        raise RuntimeError("attempt to use module that failed to load") from self.exc

class NumpyUnavailable(object):
    def __getattr__(self, key):
        raise RuntimeError("numpy is not installed")

try:
    import numpy
    NUMPY_AVAILABLE = True
except ImportError as e:
    numpy = UnavailableModule(e)
    NUMPY_AVAILABLE = False
    
np = numpy

__all__ = ['np']

if not NUMPY_AVAILABLE:
    # Put a few things in the namespace so downstream code looks normal
    np.ndarray = NumpyUnavailable()

