"""GPU matrix helpers backed by CuPy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class CupyMatrixEngine:
    """Matrix operations that are executed through CuPy on GPU."""

    def __init__(self, cp_module: Any | None = None) -> None:
        if cp_module is not None:
            self.cp = cp_module
            return

        try:
            import cupy as cp  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "CuPy is required for GPU-first matrix math. Install cupy for your CUDA runtime."
            ) from exc

        self.cp = cp

    def compose(self, *matrices: Any) -> Any:
        if not matrices:
            return self.identity()

        result = matrices[0]
        for matrix in matrices[1:]:
            result = self.cp.matmul(result, matrix)
        return result

    def identity(self) -> Any:
        return self.cp.array(
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            dtype=self.cp.float32,
        )

    def translation(self, x: float, y: float) -> Any:
        return self.cp.array(
            [[1.0, 0.0, x], [0.0, 1.0, y], [0.0, 0.0, 1.0]],
            dtype=self.cp.float32,
        )

    def scale(self, sx: float, sy: float) -> Any:
        return self.cp.array(
            [[sx, 0.0, 0.0], [0.0, sy, 0.0], [0.0, 0.0, 1.0]],
            dtype=self.cp.float32,
        )

    def rotation_degrees(self, degrees: float) -> Any:
        radians = degrees * 3.141592653589793 / 180.0
        cosine = self.cp.cos(radians)
        sine = self.cp.sin(radians)
        return self.cp.array(
            [[cosine, -sine, 0.0], [sine, cosine, 0.0], [0.0, 0.0, 1.0]],
            dtype=self.cp.float32,
        )

    def transform_points(self, points: Any, transform: Any) -> Any:
        return self.cp.matmul(points, transform.T)


@dataclass(frozen=True)
class Transform2D:
    """Immutable 2D transform represented by a 3x3 matrix."""

    engine: CupyMatrixEngine
    matrix: Any

    @classmethod
    def identity(cls, engine: CupyMatrixEngine) -> "Transform2D":
        return cls(engine=engine, matrix=engine.identity())

    def translate(self, x: float, y: float) -> "Transform2D":
        return Transform2D(self.engine, self.engine.compose(self.matrix, self.engine.translation(x, y)))

    def rotate_degrees(self, degrees: float) -> "Transform2D":
        return Transform2D(
            self.engine,
            self.engine.compose(self.matrix, self.engine.rotation_degrees(degrees)),
        )

    def scale(self, sx: float, sy: float) -> "Transform2D":
        return Transform2D(self.engine, self.engine.compose(self.matrix, self.engine.scale(sx, sy)))

    def apply_points(self, points: Any) -> Any:
        return self.engine.transform_points(points, self.matrix)
