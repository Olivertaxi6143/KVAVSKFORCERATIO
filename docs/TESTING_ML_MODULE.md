# Módulo Testing & ML

## Descripción
Módulo dedicado a la validación avanzada y machine learning para QVA Strategy Studio. Incluye validaciones temporales, pruebas automáticas y utilidades de ML para robustez de estrategias.

## Componentes

### advanced_ml_validation.py
- Validación avanzada con machine learning
- Pruebas de robustez y walk-forward
- Monte Carlo y validaciones cruzadas
- Métricas de performance ML

### advanced_temporal_validation.py
- Validación temporal avanzada
- Split IS/OOS, walk-forward, rolling windows
- Análisis de estabilidad temporal
- Generación de reportes de validación

## Funcionalidades Principales

### Validación Avanzada
- Pruebas automáticas de robustez
- Validación cruzada temporal
- Monte Carlo para stress testing
- Walk-forward analysis

### Machine Learning
- Cálculo de métricas ML
- Integración con pipelines de análisis
- Evaluación de modelos predictivos

### Testing
- Pruebas automáticas con pytest
- Tests de regresión y cobertura
- Validación de resultados y métricas

## Uso

```python
from src.ml.advanced_ml_validation import MLValidator
from src.validation.advanced_temporal_validation import TemporalValidator

ml_validator = MLValidator()
ml_results = ml_validator.validate(df)

temporal_validator = TemporalValidator()
temporal_results = temporal_validator.validate(df)
```

## Dependencias
- pandas
- numpy
- scikit-learn
- pytest

## Tests
- Validación de robustez ML
- Tests de validación temporal
- Pruebas automáticas de regresión
- Cobertura de métricas ML 