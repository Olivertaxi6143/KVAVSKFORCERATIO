
#!/usr/bin/env python3
"""
Script de verificación para comprobar que las correcciones funcionan correctamente.
"""

import sys
import subprocess
import logging

def verificar_pyright():
    """Ejecuta Pyright para verificar que no hay errores de tipo."""
    try:
        result = subprocess.run(
            ["pyright", "src/"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("[OK] Pyright: Sin errores de tipo")
            return True
        else:
            print(f"[ERROR] Pyright: Errores encontrados")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"[ERROR] Error ejecutando Pyright: {e}")
        return False

def verificar_tests():
    """Ejecuta los tests para verificar que todo funciona."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("[OK] Tests: Todos pasaron")
            return True
        else:
            print(f"[ERROR] Tests: Algunos fallaron")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"[ERROR] Error ejecutando tests: {e}")
        return False

if __name__ == "__main__":
    print("Verificando correcciones...")
    
    pyright_ok = verificar_pyright()
    tests_ok = verificar_tests()
    
    if pyright_ok and tests_ok:
        print("Todas las verificaciones pasaron!")
        sys.exit(0)
    else:
        print("Algunas verificaciones fallaron")
        sys.exit(1)
