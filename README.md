# GUI2

GUI2 is a GPU-first game GUI library scaffold.

## Design goals

- **pywin32 + ModernGL backend** for native Windows rendering
- **CuPy matrix math** for transform operations
- **Scratch-inspired object layer** through `Object` + `ObjectGroup`
- Keep game math on GPU-oriented array operations (`matmul`, transform matrices)
- Auto status transitions for `active`, `out_of_screen`, and `hidden`

## Quick example

```python
from gui2.backend import Win32ModernglBackend
from gui2.gpu_math import CupyMatrixEngine, Transform2D
from gui2.scratch import Object, ObjectGroup

backend = Win32ModernglBackend()
ctx = backend.create_gl_context()

engine = CupyMatrixEngine()
transform = Transform2D.identity(engine).translate(5, 3).rotate_degrees(15)

group = ObjectGroup().set_viewport(0, 0, 1280, 720)
player = Object().set_size(64, 64).set_position(200, 150)
group.add(player)

def clicked():
    print("clicked")

player.on_click(clicked)

player.hide()
player.set_meta("x", 300)  # metadata still updates while hidden
player.show()              # object returns as active/out_of_screen based on viewport
```

## Tests

```bash
python -m unittest discover -s tests -v
```
