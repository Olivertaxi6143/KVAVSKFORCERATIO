# KVAVSKFORCERATIO

Sistema avanzado de análisis y ranking de estrategias de trading con inteligencia artificial y arquitectura modular profesional.

## Descripción

KVAVSKFORCERATIO es una plataforma integral para el análisis, evaluación y ranking de estrategias de trading. El sistema combina análisis técnico avanzado, machine learning, predictibilidad IS/OOS y asesoramiento financiero inteligente para optimizar la selección de estrategias de trading.

## Características Principales

- **Análisis Avanzado de KPIs**: Evaluación exhaustiva de indicadores clave de rendimiento
- **Ranking Inteligente**: Sistema de clasificación basado en múltiples criterios
- **Predictibilidad IS/OOS**: Análisis de consistencia in-sample y out-of-sample
- **Asesor Financiero IA**: Recomendaciones personalizadas basadas en análisis de datos
- **Interfaz Gráfica Profesional**: GUI intuitiva con badges visuales y fila sticky
- **CLI Profesional**: Interfaz de línea de comandos para automatización
- **Arquitectura Modular**: Estructura limpia y mantenible con separación de responsabilidades
- **Sistema Libre de Errores**: 0 warnings, 0 errores, 100% tests pasando

## Estructura del Proyecto

```
KVAVSKFORCERATIO/
├── src/                    # Código fuente principal
│   ├── core/              # Motor central modular
│   │   ├── analysis/      # Módulos de análisis
│   │   │   ├── factor_k_analyzer.py
│   │   │   ├── qva_analyzer.py
│   │   │   └── unified_evaluator.py
│   │   ├── config/        # Configuración
│   │   │   ├── config_manager.py
│   │   │   ├── progress_callback.py
│   │   │   └── kpi_config.py
│   │   ├── utils/         # Utilidades
│   │   │   ├── data_utils.py
│   │   │   ├── error_handler.py
│   │   │   ├── type_converters.py
│   │   │   └── validation_utils.py
│   │   └── integration_layer.py # Capa de integración
│   ├── data/              # Gestión de datos
│   ├── gui/               # Interfaz gráfica
│   └── ml/                # Machine learning
├── config/                 # Configuraciones
├── tests/                  # Tests automatizados
├── docs/                   # Documentación completa
├── main.py                 # Punto de entrada principal
├── run_gui.py             # Lanzador de interfaz gráfica
├── cli_asesor_financiero.py # CLI principal
└── requirements.txt        # Dependencias
```

## Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/Olivertaxi6143/KVAVSKFORCERATIO.git
cd KVAVSKFORCERATIO
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

## Uso

### Interfaz Gráfica
```bash
python run_gui.py
```

### Línea de Comandos
```bash
python cli_asesor_financiero.py
```

### Análisis Completo
```bash
python run_full_cli_workflow.py
```

### Tests de Integración
```bash
python -m pytest test_integration_layer.py -v
```

## Configuración

El archivo `config/trading_config.json` contiene las configuraciones principales del sistema:

- Parámetros de análisis
- Configuración de KPIs
- Rutas de archivos de datos
- Configuración de estrategias
- Métricas de predictibilidad

## Tests

Ejecutar tests automatizados:
```bash
python -m pytest tests/
```

Ejecutar tests de integración específicos:
```bash
python -m pytest test_integration_layer.py -v
```

## Dependencias Principales

- pandas: Análisis de datos
- numpy: Cálculos numéricos
- tkinter: Interfaz gráfica
- matplotlib: Visualizaciones
- scikit-learn: Machine learning
- pytest: Testing
- scipy: Análisis estadístico

## Estado Actual del Proyecto

### ✅ Completado (8/9 fases)
1. **Análisis de Datos Empíricos Reales** ✅
2. **Implementación en DarwinEX Pipeline** ✅
3. **Implementación en Axi Select Pipeline** ✅
4. **Implementación en Asesor Financiero** ✅
5. **Integración y Testing** ✅
6. **Mejoras de Interfaz y Usabilidad** ✅
7. **Modularización del Core Engine** ✅
8. **Corrección Profesional de Errores y Warnings** ✅

### ⏳ Pendiente (1/9 fases)
9. **Documentación y GUI Final** ⏳

### 📊 Métricas de Éxito
- **Tests unitarios**: 100% pasando (18/18)
- **Warnings**: 0 (todos corregidos)
- **Errores**: 0 (todos resueltos)
- **Predictibilidad promedio**: 73.0 (excelente)
- **Arquitectura modular**: ✅ Implementada
- **Sistema limpio**: ✅ Sin warnings ni errores

## Licencia

Este proyecto es propiedad de Oliver Taxi 6143.

## Contacto

Para soporte técnico o consultas sobre el proyecto, contactar al desarrollador principal.

## Changelog

### Versión Actual (v2.0)
- ✅ Sistema completo de análisis de estrategias
- ✅ GUI profesional con badges visuales y fila sticky
- ✅ CLI avanzado con asesoramiento IA
- ✅ Tests automatizados completos (18/18 pasando)
- ✅ Arquitectura modular profesional
- ✅ Corrección completa de errores y warnings
- ✅ Documentación exhaustiva
- ✅ Análisis de predictibilidad IS/OOS
- ✅ Sistema libre de errores (0 warnings, 0 errores)
 