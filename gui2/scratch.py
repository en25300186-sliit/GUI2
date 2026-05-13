"""Scratch-inspired object model for high-level gameplay logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


STATUS_ACTIVE = "active"
STATUS_OUT_OF_SCREEN = "out_of_screen"
STATUS_HIDDEN = "hidden"


@dataclass
class Object:
    """Base object with reactive metadata and runtime status."""

    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = STATUS_ACTIVE
    _viewport: tuple[float, float, float, float] = (0.0, 0.0, 800.0, 600.0)
    _hidden: bool = False
    _gui_sync_hook: Callable[["Object"], None] | None = None

    def __post_init__(self) -> None:
        self.metadata.setdefault("x", 0.0)
        self.metadata.setdefault("y", 0.0)
        self.metadata.setdefault("width", 1.0)
        self.metadata.setdefault("height", 1.0)
        self._update_status_from_viewport()

    def bind_gui_sync(self, hook: Callable[["Object"], None]) -> "Object":
        self._gui_sync_hook = hook
        return self

    def set_meta(self, key: str, value: Any) -> "Object":
        self.metadata[key] = value
        if key in {"x", "y", "width", "height"}:
            self._update_status_from_viewport()
        self._notify_gui_sync()
        return self

    def get_meta(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    def set_position(self, x: float, y: float) -> "Object":
        self.metadata["x"] = x
        self.metadata["y"] = y
        self._update_status_from_viewport()
        self._notify_gui_sync()
        return self

    def set_size(self, width: float, height: float) -> "Object":
        self.metadata["width"] = max(0.0, width)
        self.metadata["height"] = max(0.0, height)
        self._update_status_from_viewport()
        self._notify_gui_sync()
        return self

    def set_viewport(self, x: float, y: float, width: float, height: float) -> "Object":
        self._viewport = (x, y, width, height)
        self._update_status_from_viewport()
        self._notify_gui_sync()
        return self

    def hide(self) -> "Object":
        self._hidden = True
        self.status = STATUS_HIDDEN
        self._notify_gui_sync()
        return self

    def show(self) -> "Object":
        self._hidden = False
        self._update_status_from_viewport()
        self._notify_gui_sync()
        return self

    def on_click(self, callback: Callable[..., Any] | None = None) -> "Object" | Callable[[Callable[..., Any]], Callable[..., Any]]:
        if callback is not None:
            self.metadata["on_click"] = callback
            self._notify_gui_sync()
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.metadata["on_click"] = fn
            self._notify_gui_sync()
            return fn

        return decorator

    def on_collide(
        self, callback: Callable[..., Any] | None = None
    ) -> "Object" | Callable[[Callable[..., Any]], Callable[..., Any]]:
        if callback is not None:
            self.metadata["on_collide"] = callback
            self._notify_gui_sync()
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.metadata["on_collide"] = fn
            self._notify_gui_sync()
            return fn

        return decorator

    def trigger_click(self, *args: Any, **kwargs: Any) -> Any:
        callback = self.metadata.get("on_click")
        # Disabled when hidden/out_of_screen to skip GUI interaction math.
        if callback is None or self.status != STATUS_ACTIVE:
            return None
        return callback(*args, **kwargs)

    def trigger_collide(self, *args: Any, **kwargs: Any) -> Any:
        callback = self.metadata.get("on_collide")
        # Disabled when hidden/out_of_screen to skip GUI interaction math.
        if callback is None or self.status != STATUS_ACTIVE:
            return None
        return callback(*args, **kwargs)

    def _notify_gui_sync(self) -> None:
        if self._gui_sync_hook is not None:
            self._gui_sync_hook(self)

    def _update_status_from_viewport(self) -> None:
        if self._hidden:
            self.status = STATUS_HIDDEN
            return

        x = float(self.metadata.get("x", 0.0))
        y = float(self.metadata.get("y", 0.0))
        width = max(0.0, float(self.metadata.get("width", 0.0)))
        height = max(0.0, float(self.metadata.get("height", 0.0)))
        viewport_x, viewport_y, viewport_width, viewport_height = self._viewport

        outside = (
            x + width < viewport_x
            or x > viewport_x + viewport_width
            or y + height < viewport_y
            or y > viewport_y + viewport_height
        )
        self.status = STATUS_OUT_OF_SCREEN if outside else STATUS_ACTIVE


@dataclass
class ObjectGroup(Object):
    """Group object that is also an object and manages child objects."""

    children: list[Object] = field(default_factory=list)

    def add(self, child: Object) -> "ObjectGroup":
        self.children.append(child)
        child.set_viewport(*self._viewport)
        self._notify_gui_sync()
        return self

    def remove(self, child: Object) -> "ObjectGroup":
        self.children.remove(child)
        self._notify_gui_sync()
        return self

    def set_viewport(self, x: float, y: float, width: float, height: float) -> "ObjectGroup":
        super().set_viewport(x, y, width, height)
        for child in self.children:
            child.set_viewport(x, y, width, height)
        return self
