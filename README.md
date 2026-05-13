# GUI2

GUI2 is a GPU-first game GUI library scaffold.

## Design goals

- **pywin32 + ModernGL backend** for native Windows rendering
- **CuPy matrix math** for transform operations
- **Scratch-like top layer** through a block API (`Stage` + `ScriptBuilder`)
- Keep game math on GPU-oriented array operations (`matmul`, transform matrices)

## Quick example

```python
from gui2.backend import Win32ModernglBackend
from gui2.gpu_math import CupyMatrixEngine, Transform2D
from gui2.scratch import Stage

backend = Win32ModernglBackend()
ctx = backend.create_gl_context()

engine = CupyMatrixEngine()
transform = Transform2D.identity(engine).translate(5, 3).rotate_degrees(15)

stage = Stage()
stage.when_flag_clicked().move_steps(10).turn_right_degrees(15).say("Hi")
```

## Tests

```bash
python -m unittest discover -s tests -v
```
