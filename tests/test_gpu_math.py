import unittest

from gui2.gpu_math import CupyMatrixEngine, Transform2D


class FakeArray:
    def __init__(self, data):
        self.data = data

    @property
    def T(self):
        rows = len(self.data)
        cols = len(self.data[0])
        return FakeArray([[self.data[r][c] for r in range(rows)] for c in range(cols)])


class FakeCuPy:
    float32 = "float32"

    @staticmethod
    def array(data, dtype=None):
        return FakeArray(data)

    @staticmethod
    def cos(value):
        return __import__("math").cos(value)

    @staticmethod
    def sin(value):
        return __import__("math").sin(value)

    @staticmethod
    def matmul(left, right):
        left_rows = len(left.data)
        left_cols = len(left.data[0])
        right_cols = len(right.data[0])
        out = [[0.0 for _ in range(right_cols)] for _ in range(left_rows)]
        for i in range(left_rows):
            for j in range(right_cols):
                for k in range(left_cols):
                    out[i][j] += left.data[i][k] * right.data[k][j]
        return FakeArray(out)


class TestGpuMath(unittest.TestCase):
    def test_transform_chain(self):
        engine = CupyMatrixEngine(cp_module=FakeCuPy())
        transform = Transform2D.identity(engine).translate(5, 0).scale(2, 2)
        points = FakeCuPy.array([[1.0, 1.0, 1.0]])
        transformed = transform.apply_points(points)
        self.assertEqual(transformed.data, [[7.0, 2.0, 1.0]])

    def test_rotation_90_degrees(self):
        engine = CupyMatrixEngine(cp_module=FakeCuPy())
        transform = Transform2D.identity(engine).rotate_degrees(90)
        points = FakeCuPy.array([[1.0, 0.0, 1.0]])
        transformed = transform.apply_points(points)
        self.assertAlmostEqual(transformed.data[0][0], 0.0, places=5)
        self.assertAlmostEqual(transformed.data[0][1], 1.0, places=5)
        self.assertEqual(transformed.data[0][2], 1.0)


if __name__ == "__main__":
    unittest.main()
