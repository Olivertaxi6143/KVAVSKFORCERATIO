# KVAVSKFORCERATIO

Sistema avanzado de análisis y ranking de estrategias de trading con inteligencia artificial.

## Descripción

KVAVSKFORCERATIO es una plataforma integral para el análisis, evaluación y ranking de estrategias de trading. El sistema combina análisis técnico avanzado, machine learning y asesoramiento financiero inteligente para optimizar la selección de estrategias de trading.

## Características Principales

- **Análisis Avanzado de KPIs**: Evaluación exhaustiva de indicadores clave de rendimiento
- **Ranking Inteligente**: Sistema de clasificación basado en múltiples criterios
- **Asesor Financiero IA**: Recomendaciones personalizadas basadas en análisis de datos
- **Interfaz Gráfica**: GUI intuitiva para visualización y análisis
- **CLI Profesional**: Interfaz de línea de comandos para automatización
- **Análisis IS/OOS**: Validación in-sample y out-of-sample de estrategias

## Estructura del Proyecto

```
KVAVSKFORCERATIO/
├── src/                    # Código fuente principal
│   ├── core_engine_enhanced.py
│   ├── data_manager.py
│   ├── advanced_analysis_enhanced.py
│   └── asesor_financiero_inteligente.py
├── config/                 # Configuraciones
├── tests/                  # Tests automatizados
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

## Configuración

El archivo `config/trading_config.json` contiene las configuraciones principales del sistema:

- Parámetros de análisis
- Configuración de KPIs
- Rutas de archivos de datos
- Configuración de estrategias

## Tests

Ejecutar tests automatizados:
```bash
python -m pytest tests/
```

## Dependencias Principales

- pandas: Análisis de datos
- numpy: Cálculos numéricos
- tkinter: Interfaz gráfica
- matplotlib: Visualizaciones
- scikit-learn: Machine learning
- pytest: Testing

## Licencia

Este proyecto es propiedad de Oliver Taxi 6143.

## Contacto

Para soporte técnico o consultas sobre el proyecto, contactar al desarrollador principal.

## Changelog

### Versión Actual
- Sistema completo de análisis de estrategias
- GUI profesional con múltiples pestañas
- CLI avanzado con asesoramiento IA
- Tests automatizados completos
- Documentación exhaustiva
