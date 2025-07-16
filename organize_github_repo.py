#!/usr/bin/env python3
"""
Script para organizar el repositorio de GitHub KVAVSKFORCERATIO
Organiza el proyecto en ramas modulares y actualiza la main con la estructura completa.

Autor: Sistema de Migración Profesional
Fecha: 2025-01-09
Versión: 2.1
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import json

class GitHubRepoOrganizer:
    """Organizador profesional del repositorio GitHub."""
    
    def __init__(self):
        self.repo_path = Path.cwd()
        self.branches = {
            'main': {
                'description': 'Rama principal con estructura completa del proyecto',
                'files': [
                    'main.py', 'setup.py', 'requirements.txt', 'README.md',
                    'src/', 'tests/', 'docs/', 'config/', 'exports/',
                    'run_*.py', 'run_*.bat', 'run_*.sh'
                ]
            },
            'data': {
                'description': 'Módulo de gestión de datos y procesamiento',
                'files': [
                    'src/data/', 'tests/test_data_*.py', 'tests/test_*data*.py'
                ]
            },
            'gui': {
                'description': 'Módulo de interfaz gráfica y componentes visuales',
                'files': [
                    'src/gui/', 'tests/test_gui_*.py', 'tests/test_*gui*.py'
                ]
            },
            'core': {
                'description': 'Módulo de motor de análisis y lógica de negocio',
                'files': [
                    'src/core/', 'tests/test_core_*.py', 'tests/test_*core*.py',
                    'tests/test_integration_layer.py', 'tests/test_factor_k_*.py',
                    'tests/test_qva_*.py', 'tests/test_unified_*.py'
                ]
            },
            'analysis': {
                'description': 'Módulo de análisis avanzado y métricas científicas',
                'files': [
                    'src/analysis/', 'tests/test_analysis_*.py', 'tests/test_*analysis*.py'
                ]
            },
            'ml': {
                'description': 'Módulo de machine learning y validación avanzada',
                'files': [
                    'src/ml/', 'tests/test_ml_*.py', 'tests/test_*ml*.py'
                ]
            }
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command: str, check: bool = True) -> bool:
        """Ejecutar comando de git con manejo de errores."""
        try:
            self.log(f"Ejecutando: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0 and check:
                self.log(f"Error en comando: {result.stderr}", "ERROR")
                return False
            
            if result.stdout.strip():
                self.log(f"Salida: {result.stdout.strip()}")
            
            return True
        except Exception as e:
            self.log(f"Excepción en comando: {e}", "ERROR")
            return False
    
    def check_git_status(self) -> bool:
        """Verificar estado de git."""
        self.log("Verificando estado de Git...")
        
        # Verificar si estamos en un repositorio git
        if not self.run_command("git status", check=False):
            self.log("No es un repositorio Git válido", "ERROR")
            return False
        
        # Verificar si hay cambios pendientes
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            self.log("Hay cambios pendientes. Haciendo commit...")
            if not self.run_command("git add ."):
                return False
            if not self.run_command('git commit -m "feat: actualización antes de organización de ramas"'):
                return False
        
        return True
    
    def create_branch_structure(self):
        """Crear estructura de ramas modulares."""
        self.log("Creando estructura de ramas modulares...")
        
        # Asegurar que estamos en main
        if not self.run_command("git checkout main"):
            return False
        
        # Crear ramas para cada módulo
        for branch_name, branch_info in self.branches.items():
            if branch_name == 'main':
                continue
                
            self.log(f"Creando rama: {branch_name}")
            
            # Crear rama desde main
            if not self.run_command(f"git checkout -b {branch_name}"):
                self.log(f"Error creando rama {branch_name}", "ERROR")
                continue
            
            # Limpiar rama para contener solo archivos del módulo
            if not self.clean_branch_for_module(branch_name, branch_info['files']):
                self.log(f"Error limpiando rama {branch_name}", "ERROR")
                continue
            
            # Commit de la limpieza
            if not self.run_command(f'git add . && git commit -m "feat: estructura modular para {branch_name}"'):
                self.log(f"Error en commit de {branch_name}", "ERROR")
                continue
            
            # Volver a main
            if not self.run_command("git checkout main"):
                return False
        
        self.log("Estructura de ramas creada exitosamente")
        return True
    
    def clean_branch_for_module(self, branch_name: str, allowed_files: list):
        """Limpiar rama para contener solo archivos del módulo."""
        self.log(f"Limpiando rama {branch_name} para módulo...")
        
        # Obtener lista de archivos actuales
        result = subprocess.run("git ls-files", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        current_files = result.stdout.strip().split('\n')
        
        # Determinar archivos a mantener
        files_to_keep = []
        for pattern in allowed_files:
            if pattern.endswith('/'):
                # Es un directorio
                dir_path = pattern.rstrip('/')
                for file in current_files:
                    if file.startswith(dir_path):
                        files_to_keep.append(file)
            elif pattern.startswith('tests/test_'):
                # Es un archivo de test específico
                for file in current_files:
                    if file.startswith(pattern):
                        files_to_keep.append(file)
            else:
                # Es un archivo específico
                if pattern in current_files:
                    files_to_keep.append(file)
        
        # Agregar archivos esenciales
        essential_files = [
            'README.md', '.gitignore', 'requirements.txt', 'setup.py'
        ]
        for file in essential_files:
            if file in current_files:
                files_to_keep.append(file)
        
        # Eliminar archivos no necesarios
        files_to_remove = []
        for file in current_files:
            if file not in files_to_keep and not file.startswith('.git'):
                files_to_remove.append(file)
        
        # Eliminar archivos
        for file in files_to_remove:
            try:
                os.remove(file)
                self.log(f"Eliminado: {file}")
            except Exception as e:
                self.log(f"Error eliminando {file}: {e}", "WARNING")
        
        return True
    
    def update_main_branch(self):
        """Actualizar rama main con estructura completa."""
        self.log("Actualizando rama main...")
        
        if not self.run_command("git checkout main"):
            return False
        
        # Asegurar que main tiene todos los archivos
        if not self.run_command("git add ."):
            return False
        
        if not self.run_command('git commit -m "feat: estructura completa del proyecto en main"'):
            return False
        
        self.log("Rama main actualizada exitosamente")
        return True
    
    def create_documentation(self):
        """Crear documentación de la organización."""
        self.log("Creando documentación de organización...")
        
        doc_content = f"""# ORGANIZACIÓN DEL REPOSITORIO KVAVSKFORCERATIO

## Estructura de Ramas

### Rama Principal: `main`
- **Descripción**: Estructura completa del proyecto
- **Contenido**: Todos los archivos del proyecto organizados
- **Uso**: Desarrollo principal y releases

### Rama de Datos: `data`
- **Descripción**: Módulo de gestión de datos y procesamiento
- **Contenido**: 
  - `src/data/`
  - Tests relacionados con datos
- **Uso**: Desarrollo específico de funcionalidades de datos

### Rama de GUI: `gui`
- **Descripción**: Módulo de interfaz gráfica y componentes visuales
- **Contenido**:
  - `src/gui/`
  - Tests de GUI
- **Uso**: Desarrollo de interfaz de usuario

### Rama de Core: `core`
- **Descripción**: Módulo de motor de análisis y lógica de negocio
- **Contenido**:
  - `src/core/`
  - Tests de core engine
  - Tests de integración
- **Uso**: Desarrollo del motor de análisis

### Rama de Análisis: `analysis`
- **Descripción**: Módulo de análisis avanzado y métricas científicas
- **Contenido**:
  - `src/analysis/`
  - Tests de análisis
- **Uso**: Desarrollo de métricas y análisis

### Rama de ML: `ml`
- **Descripción**: Módulo de machine learning y validación avanzada
- **Contenido**:
  - `src/ml/`
  - Tests de ML
- **Uso**: Desarrollo de algoritmos de ML

## Flujo de Trabajo

1. **Desarrollo en ramas específicas**: Cada desarrollador trabaja en su rama correspondiente
2. **Merge a main**: Los cambios se integran a main cuando están listos
3. **Releases desde main**: Las versiones se etiquetan desde main

## Comandos Útiles

```bash
# Cambiar a rama específica
git checkout data
git checkout gui
git checkout core
git checkout analysis
git checkout ml

# Ver estado de todas las ramas
git branch -a

# Merge de rama específica a main
git checkout main
git merge data

# Push de todas las ramas
git push origin --all
```

## Fecha de Organización
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Versión
2.1 - Migración completa a arquitectura modular
"""
        
        with open('ESTRUCTURA_REPOSITORIO.md', 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        self.log("Documentación creada: ESTRUCTURA_REPOSITORIO.md")
        return True
    
    def push_to_github(self):
        """Hacer push de todas las ramas a GitHub."""
        self.log("Haciendo push de todas las ramas a GitHub...")
        
        # Push de main
        if not self.run_command("git push origin main"):
            self.log("Error haciendo push de main", "ERROR")
            return False
        
        # Push de todas las ramas
        for branch_name in self.branches.keys():
            if branch_name != 'main':
                if not self.run_command(f"git push origin {branch_name}"):
                    self.log(f"Error haciendo push de {branch_name}", "ERROR")
                    continue
        
        self.log("Push completado exitosamente")
        return True
    
    def create_summary_report(self):
        """Crear reporte de resumen de la organización."""
        self.log("Creando reporte de resumen...")
        
        report = {
            'fecha_organizacion': datetime.now().isoformat(),
            'ramas_creadas': list(self.branches.keys()),
            'archivos_por_rama': {},
            'estado': 'completado'
        }
        
        # Contar archivos por rama
        for branch_name, branch_info in self.branches.items():
            if branch_name == 'main':
                continue
            
            file_count = 0
            for pattern in branch_info['files']:
                if pattern.endswith('/'):
                    # Contar archivos en directorio
                    dir_path = pattern.rstrip('/')
                    if os.path.exists(dir_path):
                        for root, dirs, files in os.walk(dir_path):
                            file_count += len(files)
                else:
                    # Archivo específico
                    if os.path.exists(pattern):
                        file_count += 1
            
            report['archivos_por_rama'][branch_name] = file_count
        
        # Guardar reporte
        with open('REPORTE_ORGANIZACION.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log("Reporte guardado: REPORTE_ORGANIZACION.json")
        return True
    
    def organize_repository(self):
        """Proceso completo de organización del repositorio."""
        self.log("INICIANDO ORGANIZACIÓN DEL REPOSITORIO")
        self.log("=" * 50)
        
        steps = [
            ("Verificando estado de Git", self.check_git_status),
            ("Creando estructura de ramas", self.create_branch_structure),
            ("Actualizando rama main", self.update_main_branch),
            ("Creando documentación", self.create_documentation),
            ("Creando reporte de resumen", self.create_summary_report),
            ("Haciendo push a GitHub", self.push_to_github)
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            self.log(f"Ejecutando: {step_name}")
            try:
                results[step_name] = step_func()
                if results[step_name]:
                    self.log(f"✅ {step_name} completado")
                else:
                    self.log(f"❌ {step_name} falló")
            except Exception as e:
                self.log(f"❌ {step_name} falló con error: {e}", "ERROR")
                results[step_name] = False
        
        # Resumen final
        self.log("=" * 50)
        self.log("RESUMEN DE ORGANIZACIÓN")
        self.log("=" * 50)
        
        successful_steps = sum(results.values())
        total_steps = len(results)
        
        for step_name, result in results.items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            self.log(f"{step_name}: {status}")
        
        self.log(f"Total: {successful_steps}/{total_steps} pasos completados exitosamente")
        
        if successful_steps == total_steps:
            self.log("🎉 ¡ORGANIZACIÓN COMPLETADA EXITOSAMENTE!")
            self.log("El repositorio está listo para desarrollo modular")
        else:
            self.log("⚠️ ORGANIZACIÓN COMPLETADA CON ERRORES")
            self.log("Revisar los errores anteriores")
        
        return successful_steps == total_steps

def main():
    """Función principal."""
    print("=" * 60)
    print("ORGANIZADOR DE REPOSITORIO GITHUB KVAVSKFORCERATIO")
    print("=" * 60)
    
    organizer = GitHubRepoOrganizer()
    success = organizer.organize_repository()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 