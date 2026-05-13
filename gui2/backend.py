"""Native Windows + ModernGL backend wiring."""

from __future__ import annotations

from typing import Any


class Win32ModernglBackend:
    """Backend shell that combines pywin32 windowing with a ModernGL context."""

    def __init__(self, win32gui_module: Any | None = None, moderngl_module: Any | None = None) -> None:
        self.win32gui = win32gui_module
        self.moderngl = moderngl_module

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

    def create_gl_context(self) -> Any:
        return self.moderngl.create_context(require=330)
