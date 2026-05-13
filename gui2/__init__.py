"""GPU-first game GUI primitives with a Scratch-inspired object layer."""

from .backend import Win32ModernglBackend
from .gpu_math import CupyMatrixEngine, Transform2D
from .scratch import (
    STATUS_ACTIVE,
    STATUS_HIDDEN,
    STATUS_OUT_OF_SCREEN,
    Object,
    ObjectGroup,
)

__all__ = [
    "CupyMatrixEngine",
    "Object",
    "ObjectGroup",
    "STATUS_ACTIVE",
    "STATUS_HIDDEN",
    "STATUS_OUT_OF_SCREEN",
    "Transform2D",
    "Win32ModernglBackend",
]
