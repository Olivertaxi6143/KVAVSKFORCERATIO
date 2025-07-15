# ORGANIZACIÓN DEL REPOSITORIO KVAVSKFORCERATIO

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
2025-07-13 23:39:25

## Versión
2.1 - Migración completa a arquitectura modular
