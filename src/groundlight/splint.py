"""
splint.py contains some small bit to keep this slightly divergent fork straight and working
"""

from enum import Enum


class ModeEnumSplint(str, Enum):
    BINARY = "BINARY"
    COUNT = "COUNT"
    MULTI_CLASS = "MULTI_CLASS"
    TEXT = "TEXT"
    BOUNDING_BOX = "BOUNDING_BOX"
