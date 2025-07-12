# 🌿 ESTRATEGIA DE BRANCHES - KFORCEVSQVARATIOS v2.0

## 🎯 Resumen Ejecutivo

Esta estrategia de branches está diseñada para **organizar el desarrollo por componentes del sistema**, permitiendo trabajo paralelo y control de calidad por áreas específicas. La estructura sigue el patrón **GitFlow** adaptado para proyectos de análisis financiero.

---

## 🏗️ Estructura de Branches

### 📋 Branches Principales

```
main                    # Rama principal - solo código estable
├── develop            # Rama de desarrollo - integración de features
├── feature/gui-*      # Mejoras de interfaz gráfica
├── feature/core-*     # Motor de análisis y lógica central
├── feature/data-*     # Gestor de datos y ETL
├── feature/analysis-* # Análisis científico y métricas avanzadas
├── testing/*          # Tests y validación
├── docs/*             # Documentación
└── hotfix/*           # Correcciones urgentes
```

---

## 🎯 Propósito de Cada Rama

### 1. **main** - Rama Principal
- **Propósito**: Código estable y listo para producción
- **Restricciones**: 
  - Solo merges desde `develop` o `hotfix/*`
  - Requiere Pull Request y revisión
  - Deploy automático a producción
- **Ejemplo de uso**: Releases oficiales

### 2. **develop** - Rama de Desarrollo
- **Propósito**: Integración de features antes de release
- **Restricciones**:
  - Merge desde `feature/*` y `testing/*`
  - Tests automáticos obligatorios
  - Validación de calidad
- **Ejemplo de uso**: Integración de nuevas funcionalidades

### 3. **feature/gui-*** - Interfaz Gráfica
- **Propósito**: Mejoras y nuevas funcionalidades de la GUI
- **Archivos principales**:
  - `src/gui_enhanced_rank.py`
  - `src/config_manager_enhanced.py`
  - Templates y assets de UI
- **Ejemplos de ramas**:
  - `feature/gui-enhancements`
  - `feature/gui-new-tabs`
  - `feature/gui-responsive-design`

### 4. **feature/core-*** - Motor de Análisis
- **Propósito**: Mejoras del motor de análisis científico
- **Archivos principales**:
  - `src/core_engine_enhanced.py`
  - `src/scientific_analysis.py`
  - Algoritmos de métricas científicas
- **Ejemplos de ramas**:
  - `feature/core-engine-improvements`
  - `feature/core-new-metrics`
  - `feature/core-performance-optimization`

### 5. **feature/data-*** - Gestión de Datos
- **Propósito**: Optimización del procesamiento de datos
- **Archivos principales**:
  - `src/data_manager.py`
  - Validaciones y limpieza de datos
  - ETL y transformaciones
- **Ejemplos de ramas**:
  - `feature/data-manager-optimization`
  - `feature/data-validation-improvements`
  - `feature/data-etl-enhancements`

### 6. **feature/analysis-*** - Análisis Avanzado
- **Propósito**: Métricas científicas y análisis avanzado
- **Archivos principales**:
  - `src/advanced_analysis_enhanced.py`
  - `src/asesor_financiero_inteligente.py`
  - Algoritmos de machine learning
- **Ejemplos de ramas**:
  - `feature/analysis-advanced-metrics`
  - `feature/analysis-ml-integration`
  - `feature/analysis-predictive-models`

### 7. **testing/*** - Tests y Validación
- **Propósito**: Tests de integración y validación
- **Archivos principales**:
  - `test_cli_flujo_completo_exhaustivo.py`
  - Tests unitarios y de integración
  - Validación de calidad
- **Ejemplos de ramas**:
  - `testing/integration-tests`
  - `testing/performance-tests`
  - `testing/quality-validation`

### 8. **docs/*** - Documentación
- **Propósito**: Actualización de documentación
- **Archivos principales**:
  - `DOCUMENTACION_FLUJO_TRABAJO.md`
  - `GUIA_INSTALACION.md`
  - `GUIA_USUARIO.md`
- **Ejemplos de ramas**:
  - `docs/update-user-guide`
  - `docs/api-documentation`
  - `docs/technical-specs`

### 9. **hotfix/*** - Correcciones Urgentes
- **Propósito**: Correcciones críticas para producción
- **Restricciones**:
  - Solo para bugs críticos
  - Merge directo a `main` y `develop`
  - Deploy inmediato
- **Ejemplos de ramas**:
  - `hotfix/critical-bug-fix`
  - `hotfix/security-patch`
  - `hotfix/performance-issue`

---

## 🔄 Flujo de Trabajo

### 1. **Desarrollo de Features**

```bash
# 1. Crear rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/gui-new-chart

# 2. Desarrollar feature
# ... hacer cambios en el código ...

# 3. Commit y push
git add .
git commit -m "feat(gui): añadir nuevo gráfico de métricas"
git push origin feature/gui-new-chart

# 4. Crear Pull Request
# Ir a GitHub y crear PR: feature/gui-new-chart → develop
```

### 2. **Integración de Features**

```bash
# 1. Merge a develop (después de aprobar PR)
git checkout develop
git pull origin develop
git merge feature/gui-new-chart

# 2. Push a develop
git push origin develop

# 3. Eliminar rama feature (opcional)
git branch -d feature/gui-new-chart
```

### 3. **Release a Producción**

```bash
# 1. Crear rama de release
git checkout develop
git checkout -b release/v2.1.0

# 2. Preparar release
# - Actualizar versiones
# - Actualizar changelog
# - Tests finales

# 3. Merge a main
git checkout main
git merge release/v2.1.0
git tag v2.1.0

# 4. Merge a develop
git checkout develop
git merge release/v2.1.0

# 5. Push
git push origin main develop
git push origin v2.1.0
```

### 4. **Hotfix Urgente**

```bash
# 1. Crear hotfix desde main
git checkout main
git checkout -b hotfix/critical-bug-fix

# 2. Corregir bug
# ... hacer corrección ...

# 3. Commit y merge
git add .
git commit -m "fix: corregir bug crítico en análisis"
git checkout main
git merge hotfix/critical-bug-fix
git tag v2.0.1

# 4. Merge a develop
git checkout develop
git merge hotfix/critical-bug-fix

# 5. Push
git push origin main develop
git push origin v2.0.1
```

---

## 📋 Convenciones de Nomenclatura

### 1. **Branches de Features**
```
feature/[componente]-[descripción]
Ejemplos:
- feature/gui-enhancements
- feature/core-engine-improvements
- feature/data-manager-optimization
- feature/analysis-advanced-metrics
```

### 2. **Branches de Testing**
```
testing/[tipo]-[descripción]
Ejemplos:
- testing/integration-tests
- testing/performance-tests
- testing/quality-validation
```

### 3. **Branches de Documentación**
```
docs/[tipo]-[descripción]
Ejemplos:
- docs/update-user-guide
- docs/api-documentation
- docs/technical-specs
```

### 4. **Branches de Hotfix**
```
hotfix/[descripción]
Ejemplos:
- hotfix/critical-bug-fix
- hotfix/security-patch
- hotfix/performance-issue
```

---

## 🎯 Estrategia por Componentes

### **GUI (Interfaz Gráfica)**
```bash
# Rama principal para GUI
feature/gui-enhancements

# Sub-ramas específicas
feature/gui-new-tabs
feature/gui-responsive-design
feature/gui-chart-improvements
feature/gui-user-experience
```

### **Core Engine (Motor de Análisis)**
```bash
# Rama principal para Core Engine
feature/core-engine-improvements

# Sub-ramas específicas
feature/core-new-metrics
feature/core-performance-optimization
feature/core-algorithm-enhancements
feature/core-scientific-analysis
```

### **Data Manager (Gestión de Datos)**
```bash
# Rama principal para Data Manager
feature/data-manager-optimization

# Sub-ramas específicas
feature/data-validation-improvements
feature/data-etl-enhancements
feature/data-cache-optimization
feature/data-error-handling
```

### **Advanced Analysis (Análisis Avanzado)**
```bash
# Rama principal para Análisis Avanzado
feature/analysis-advanced-metrics

# Sub-ramas específicas
feature/analysis-ml-integration
feature/analysis-predictive-models
feature/analysis-clustering-algorithms
feature/analysis-risk-assessment
```

---

## 🔧 Configuración Recomendada

### 1. **Git Hooks**
```bash
# Pre-commit hook para validación
#!/bin/sh
# Validar que el código pase los tests
python -m pytest tests/ -v
# Validar linting
flake8 src/
# Validar tipos
mypy src/
```

### 2. **Branch Protection Rules**
- **main**: Requiere Pull Request y revisión
- **develop**: Requiere Pull Request y tests
- **feature/***: Requiere tests antes de merge

### 3. **Automated Testing**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python -m pytest tests/ -v
      - name: Run linting
        run: flake8 src/
```

---

## 📊 Métricas de Calidad

### 1. **Code Coverage**
- Mínimo 80% de cobertura de código
- Tests unitarios para cada componente
- Tests de integración para flujos completos

### 2. **Performance**
- Tests de rendimiento en cada merge
- Monitoreo de uso de memoria
- Validación de tiempos de respuesta

### 3. **Documentation**
- Documentación actualizada en cada feature
- README actualizado
- Changelog mantenido

---

## 🚀 Comandos Útiles

### **Gestión de Branches**
```bash
# Ver todas las ramas
git branch -a

# Ver ramas por componente
git branch | grep feature/gui
git branch | grep feature/core
git branch | grep feature/data

# Eliminar ramas locales
git branch -d feature/old-feature

# Eliminar ramas remotas
git push origin --delete feature/old-feature
```

### **Trabajo con Features**
```bash
# Crear nueva feature
git checkout develop
git pull origin develop
git checkout -b feature/nueva-feature

# Actualizar feature con develop
git checkout feature/nueva-feature
git rebase develop

# Merge feature
git checkout develop
git merge feature/nueva-feature
```

### **Releases**
```bash
# Crear release
git checkout develop
git checkout -b release/v2.1.0

# Tag release
git checkout main
git merge release/v2.1.0
git tag v2.1.0
git push origin v2.1.0
```

---

## 📝 Checklist de Calidad

### **Antes de Merge a develop**
- [ ] Tests pasando (pytest)
- [ ] Linting limpio (flake8)
- [ ] Tipos validados (mypy)
- [ ] Documentación actualizada
- [ ] Código revisado por otro desarrollador

### **Antes de Release**
- [ ] Todos los tests pasando
- [ ] Performance validada
- [ ] Documentación completa
- [ ] Changelog actualizado
- [ ] Version bump realizado

### **Antes de Deploy a Producción**
- [ ] Tests de integración pasando
- [ ] Tests de performance validados
- [ ] Backup de datos realizado
- [ ] Rollback plan preparado
- [ ] Monitoreo configurado

---

## 🎯 Beneficios de esta Estrategia

### **Para el Equipo**
- **Trabajo paralelo**: Múltiples desarrolladores pueden trabajar en diferentes componentes
- **Control de calidad**: Validación específica por área
- **Escalabilidad**: Fácil añadir nuevos componentes
- **Mantenibilidad**: Código organizado y fácil de navegar

### **Para el Proyecto**
- **Estabilidad**: Código estable en main
- **Flexibilidad**: Desarrollo ágil con features aisladas
- **Trazabilidad**: Historial claro de cambios
- **Colaboración**: Pull requests y code reviews

### **Para el Negocio**
- **Rapidez**: Deploy rápido de features
- **Confiabilidad**: Menos bugs en producción
- **Escalabilidad**: Fácil añadir nuevas funcionalidades
- **Mantenimiento**: Correcciones rápidas y seguras

---

*Estrategia de Branches - KFORCEVSQVARATIOS v2.0*  
*Fecha: 2025-07-11*  
*Versión: v1.0* 