#!/usr/bin/env python3
"""
Script para crear ramas limpias desde main con solo el módulo correspondiente.
Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

import subprocess
import sys
import os

def run_command(command):
    """Ejecuta un comando y retorna el resultado."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando: {command}")
        print(f"Error: {e.stderr}")
        return None

def create_clean_branch(branch_name, module_path):
    """Crea una rama limpia con solo el módulo especificado."""
    print(f"\n🔄 Creando rama {branch_name} con módulo {module_path}...")
    
    # Cambiar a main
    run_command("git checkout main")
    
    # Crear nueva rama desde main
    if run_command(f"git checkout -b {branch_name}") is None:
        # Si la rama ya existe, cambiarla y resetear
        run_command(f"git checkout {branch_name}")
        run_command("git reset --hard main")
    
    # Eliminar todos los módulos excepto el especificado
    modules_to_remove = ["src/analysis", "src/core", "src/data", "src/gui", "src/ml"]
    if module_path in modules_to_remove:
        modules_to_remove.remove(module_path)
    
    for module in modules_to_remove:
        run_command(f"git rm -r {module}")
    
    # Eliminar carpetas adicionales
    run_command("git rm -r tests/unit docs/ config/")
    run_command("git rm *.py")
    
    # Restaurar el módulo específico
    run_command(f"git checkout HEAD -- {module_path}/")
    run_command(f"git add {module_path}/")
    
    # Commit
    commit_msg = f"feat: rama {branch_name} con solo módulo {module_path} actualizado"
    run_command(f'git commit -m "{commit_msg}"')
    
    # Push forzado
    run_command(f"git push origin {branch_name} --force")
    
    print(f"✅ Rama {branch_name} creada y subida exitosamente")

def main():
    """Función principal."""
    print("🚀 Iniciando creación de ramas limpias...")
    
    # Definir las ramas y sus módulos correspondientes
    branches = [
        ("data", "src/data"),
        ("gui", "src/gui"),
        ("ml", "src/ml"),
    ]
    
    # Crear cada rama
    for branch_name, module_path in branches:
        create_clean_branch(branch_name, module_path)
    
    # Volver a main
    run_command("git checkout main")
    
    print("\n🎉 ¡Todas las ramas han sido creadas exitosamente!")
    print("📋 Resumen de ramas creadas:")
    print("   - analysis: módulo src/analysis")
    print("   - core: módulo src/core") 
    print("   - data: módulo src/data")
    print("   - gui: módulo src/gui")
    print("   - ml: módulo src/ml")
    print("   - main: proyecto completo (rama principal)")

if __name__ == "__main__":
    main() 