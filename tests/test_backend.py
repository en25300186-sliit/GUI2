import unittest

from gui2.backend import Win32ModernglBackend


class FakeModerngl:
    @staticmethod
    def create_context(require=0):
        return {"require": require}


class FakeWin32Con:
    WM_DESTROY = 2
    WS_OVERLAPPEDWINDOW = 10
    SW_SHOW = 5
    COLOR_WINDOW = 5
    IDC_ARROW = 32512


class FakeWindowClass:
    lpfnWndProc = None
    lpszClassName = ""
    hInstance = 0
    hCursor = 0
    hbrBackground = 0


class FakeWin32Api:
    @staticmethod
    def GetModuleHandle(_):
        return 1


class FakeWin32Gui:
    def __init__(self):
        self.class_registered = False
        self.window_created = False
        self.window_shown = False
        self.window_updated = False
        self.quit_posted = False

    @staticmethod
    def WNDCLASS():
        return FakeWindowClass()

    @staticmethod
    def LoadCursor(_, __):
        return 1

    def RegisterClass(self, _):
        self.class_registered = True

    def CreateWindow(self, *_):
        self.window_created = True
        return 99

    def ShowWindow(self, *_):
        self.window_shown = True

    def UpdateWindow(self, *_):
        self.window_updated = True

    @staticmethod
    def DefWindowProc(*_):
        return 0

    @staticmethod
    def PumpWaitingMessages():
        return 0

    def PostQuitMessage(self, _):
        self.quit_posted = True


class FakeWin32GuiQuitOnFirstPump(FakeWin32Gui):
    def __init__(self):
        super().__init__()
        self.pump_calls = 0

    def PumpWaitingMessages(self):
        self.pump_calls += 1
        return 1


class TestBackend(unittest.TestCase):
    def test_backend_creates_context(self):
        backend = Win32ModernglBackend(win32gui_module=object(), moderngl_module=FakeModerngl())
        context = backend.create_gl_context()
        self.assertEqual(context["require"], 330)

    def test_backend_creates_window(self):
        win32gui = FakeWin32Gui()
        backend = Win32ModernglBackend(
            win32gui_module=win32gui,
            moderngl_module=FakeModerngl(),
            win32con_module=FakeWin32Con(),
            win32api_module=FakeWin32Api(),
        )

        hwnd = backend.create_window(title="Test Window", width=800, height=600)

        self.assertEqual(hwnd, 99)
        self.assertTrue(win32gui.class_registered)
        self.assertTrue(win32gui.window_created)
        self.assertTrue(win32gui.window_shown)
        self.assertTrue(win32gui.window_updated)

    def test_draw_window_runs_frame_callback(self):
        backend = Win32ModernglBackend(
            win32gui_module=FakeWin32Gui(),
            moderngl_module=FakeModerngl(),
            win32con_module=FakeWin32Con(),
            win32api_module=FakeWin32Api(),
        )

        frames = []
        backend.draw_window(
            title="Draw Test",
            width=640,
            height=480,
            on_frame=lambda _, idx: frames.append(idx),
            max_frames=3,
            frame_sleep_seconds=0,
        )

        self.assertEqual(frames, [0, 1, 2])

    def test_draw_window_exits_when_quit_message_is_pumped(self):
        win32gui = FakeWin32GuiQuitOnFirstPump()
        backend = Win32ModernglBackend(
            win32gui_module=win32gui,
            moderngl_module=FakeModerngl(),
            win32con_module=FakeWin32Con(),
            win32api_module=FakeWin32Api(),
        )

        frames = []
        backend.draw_window(on_frame=lambda *_: frames.append("frame"), max_frames=10, frame_sleep_seconds=0)

        self.assertEqual(frames, [])
        self.assertEqual(win32gui.pump_calls, 1)


if __name__ == "__main__":
    unittest.main()
