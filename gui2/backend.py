"""Native Windows + ModernGL backend wiring."""

from __future__ import annotations

import time
from typing import Callable
from typing import Any


class Win32ModernglBackend:
    """Backend shell that combines pywin32 windowing with a ModernGL context."""

    _SYSTEM_COLOR_BRUSH_OFFSET = 1
    _ERROR_CLASS_ALREADY_EXISTS = 1410
    _DEFAULT_FRAME_SLEEP_SECONDS = 1 / 60  # Target ~60 FPS.

    def __init__(
        self,
        win32gui_module: Any | None = None,
        moderngl_module: Any | None = None,
        win32con_module: Any | None = None,
        win32api_module: Any | None = None,
        pywintypes_module: Any | None = None,
    ) -> None:
        self.win32gui = win32gui_module
        self.moderngl = moderngl_module
        self.win32con = win32con_module
        self.win32api = win32api_module
        self.pywintypes = pywintypes_module

        if self.win32gui is None:
            try:
                import win32gui  # type: ignore
            except ImportError as exc:
                raise RuntimeError("pywin32 is required for the Win32 backend.") from exc
            self.win32gui = win32gui

        if self.moderngl is None:
            try:
                import moderngl  # type: ignore
            except ImportError as exc:
                raise RuntimeError("moderngl is required for GPU rendering.") from exc
            self.moderngl = moderngl

    def _ensure_win32_window_modules(self) -> None:
        if self.win32con is None:
            try:
                import win32con  # type: ignore
            except ImportError as exc:
                raise RuntimeError("pywin32 win32con is required to create the Win32 window.") from exc
            self.win32con = win32con

        if self.win32api is None:
            try:
                import win32api  # type: ignore
            except ImportError as exc:
                raise RuntimeError("pywin32 win32api is required to create the Win32 window.") from exc
            self.win32api = win32api

        if self.pywintypes is None:
            try:
                import pywintypes  # type: ignore
            except ImportError:
                self.pywintypes = None
            else:
                self.pywintypes = pywintypes

    def _is_class_already_exists_error(self, exc: BaseException) -> bool:
        error_code = getattr(exc, "winerror", None)
        if error_code is None and getattr(exc, "args", None):
            first_arg = exc.args[0]
            if isinstance(first_arg, int):
                error_code = first_arg
        return error_code == self._ERROR_CLASS_ALREADY_EXISTS

    def _wndproc(self, hwnd: Any, message: int, wparam: Any, lparam: Any) -> Any:
        if message == getattr(self.win32con, "WM_DESTROY", 2):
            self.win32gui.PostQuitMessage(0)
            return 0
        if hasattr(self.win32gui, "DefWindowProc"):
            return self.win32gui.DefWindowProc(hwnd, message, wparam, lparam)
        return 0

    def create_window(
        self,
        title: str = "GUI2",
        width: int = 1280,
        height: int = 720,
        x: int = 100,
        y: int = 100,
        class_name: str = "GUI2WindowClass",
    ) -> Any:
        self._ensure_win32_window_modules()

        wndclass = self.win32gui.WNDCLASS()
        wndclass.lpfnWndProc = self._wndproc
        wndclass.lpszClassName = class_name
        wndclass.hInstance = self.win32api.GetModuleHandle(None)

        if hasattr(self.win32gui, "LoadCursor"):
            wndclass.hCursor = self.win32gui.LoadCursor(0, getattr(self.win32con, "IDC_ARROW", 32512))
        # Win32 expects (COLOR_* constant + 1) when a class background uses a system color brush.
        color_window_brush = getattr(self.win32con, "COLOR_WINDOW", 5) + self._SYSTEM_COLOR_BRUSH_OFFSET
        wndclass.hbrBackground = color_window_brush

        registration_exception_types: list[type[BaseException]] = []
        win32gui_error_type = getattr(self.win32gui, "error", None)
        if isinstance(win32gui_error_type, type) and issubclass(win32gui_error_type, BaseException):
            registration_exception_types.append(win32gui_error_type)
        pywintypes_error_type = getattr(self.pywintypes, "error", None) if self.pywintypes is not None else None
        if isinstance(pywintypes_error_type, type) and issubclass(pywintypes_error_type, BaseException):
            registration_exception_types.append(pywintypes_error_type)

        if registration_exception_types:
            try:
                self.win32gui.RegisterClass(wndclass)
            except tuple(registration_exception_types) as exc:
                # Class can already exist when restarting quickly; it's safe to continue.
                if not self._is_class_already_exists_error(exc):
                    raise
        else:
            self.win32gui.RegisterClass(wndclass)

        hwnd = self.win32gui.CreateWindow(
            class_name,
            title,
            getattr(self.win32con, "WS_OVERLAPPEDWINDOW", 0),
            x,
            y,
            width,
            height,
            0,
            0,
            wndclass.hInstance,
            None,
        )
        self.win32gui.ShowWindow(hwnd, getattr(self.win32con, "SW_SHOW", 5))
        self.win32gui.UpdateWindow(hwnd)
        return hwnd

    def draw_window(
        self,
        title: str = "GUI2",
        width: int = 1280,
        height: int = 720,
        on_frame: Callable[[Any, int], None] | None = None,
        max_frames: int | None = None,
        frame_sleep_seconds: float = _DEFAULT_FRAME_SLEEP_SECONDS,
    ) -> Any:
        hwnd = self.create_window(title=title, width=width, height=height)
        frame_count = 0
        while max_frames is None or frame_count < max_frames:
            if hasattr(self.win32gui, "PumpWaitingMessages"):
                if self.win32gui.PumpWaitingMessages():
                    break

            if on_frame is not None:
                on_frame(hwnd, frame_count)

            frame_count += 1

            if frame_sleep_seconds > 0:
                time.sleep(frame_sleep_seconds)
        return hwnd

    def create_gl_context(self) -> Any:
        return self.moderngl.create_context(require=330)
