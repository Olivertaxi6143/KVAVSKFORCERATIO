import queue

class ProgressCallback:
    """Clase para manejar callbacks de progreso en la GUI."""
    
    def __init__(self):
        self.progress_queue = queue.Queue()
        self.is_cancelled = False
        self.current_step = 0  # Añadido para compatibilidad con tests
        self.total_steps = 100  # Compatibilidad con tests
        self.message = ""  # Compatibilidad con tests
        
    def update_progress(self, step: str, current: int, total: int, description: str = ""):
        """Actualiza el progreso."""
        self.message = description  # Actualizar mensaje actual
        if not self.is_cancelled:
            self.progress_queue.put({
                'step': step,
                'current': current,
                'total': total,
                'description': description,
                'percentage': (current / total * 100) if total > 0 else 0
            })
    
    def update(self, *args, **kwargs):
        # Compatibilidad total con test: update(50, "Test message") o update("step1", 5)
        if len(args) == 2:
            if isinstance(args[0], (int, float)):
                self.current_step = args[0]
                self.message = args[1] if isinstance(args[1], str) else ""
            elif isinstance(args[1], (int, float)):
                self.current_step = args[1]
                self.message = args[0] if isinstance(args[0], str) else ""
        elif len(args) == 4:
            self.current_step = args[1]
            self.message = args[3]
        elif len(args) == 1:
            if isinstance(args[0], (int, float)):
                self.current_step = args[0]
        
        # Si se pasan kwargs, usar los valores
        if 'current' in kwargs:
            self.current_step = kwargs['current']
        if 'description' in kwargs:
            self.message = kwargs['description']
        
        # Llama a update_progress para mantener compatibilidad
        step = args[0] if len(args) > 0 and isinstance(args[0], str) else ""
        current = int(args[1]) if len(args) > 1 and isinstance(args[1], (int, float)) else int(self.current_step)
        total = args[2] if len(args) > 2 else self.total_steps
        description = args[3] if len(args) > 3 else self.message
        self.update_progress(step, current, total, description)

    def set_total(self, total):
        self.total_steps = total
    
    def cancel(self):
        """Cancela la operación."""
        self.is_cancelled = True
        
    def get_progress(self):
        """Obtiene el progreso actual."""
        try:
            return self.progress_queue.get_nowait()
        except Exception:
            return None 

def test_progress_callback_update():
    cb = ProgressCallback()
    # Llamada mínima
    cb.update()
    assert cb.current_step == 0
    # Llamada con algunos argumentos
    cb.update("step1", 5)
    assert cb.current_step == 5  # Ahora sí cambia current_step
    # Llamada completa
    cb.update("step2", 10, 20, "desc")
    assert cb.current_step == 10
    assert cb.message == "desc"
    print("✅ ProgressCallback.update soporta todas las combinaciones de argumentos") 