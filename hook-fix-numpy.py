import os
import numpy as _np
# Filtrar cualquier ruta que acabe en …/numpy/numpy
_np.__path__ = [
    p for p in _np.__path__
    if os.path.basename(os.path.dirname(p)) != 'numpy'
] 