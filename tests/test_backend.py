import unittest

from gui2.backend import Win32ModernglBackend


class FakeModerngl:
    @staticmethod
    def create_context(require=0):
        return {"require": require}


class TestBackend(unittest.TestCase):
    def test_backend_creates_context(self):
        backend = Win32ModernglBackend(win32gui_module=object(), moderngl_module=FakeModerngl())
        context = backend.create_gl_context()
        self.assertEqual(context["require"], 330)


if __name__ == "__main__":
    unittest.main()
