# PLAN DE REFACTORIZACIÓN MODULAR
## Separación de core_engine_enhanced.py en Módulos Especializados

---

## 🎯 **OBJETIVO**
Refactorizar el archivo `core_engine_enhanced.py` (~4883 líneas) en módulos especializados siguiendo el principio de responsabilidad única.

---

## 📁 **ESTRUCTURA DE MÓDULOS PROPUESTA**

### **src/core/analysis/**
```
src/core/analysis/
├── __init__.py
├── factor_k_analyzer.py          # FactorKElite96Enhanced
├── qva_analyzer.py               # QVAScorerEnhanced
├── unified_scorer.py             # UnifiedEvaluatorEnhanced
├── darwin_analyzer.py            # DarwinLabsMetrics
├── darwin_pipeline.py            # DarwinEXPipelineEnhanced
└── extra_kpi_manager.py          # ExtraKPIManager
```

### **src/core/config/**
```
src/core/config/
├── __init__.py
├── config_manager.py              # ConfigManagerEnhanced
├── kpi_config.py                  # KPIConfig, TradingStyleConfig
└── progress_callback.py           # ProgressCallback
```

### **src/core/validation/**
```
src/core/validation/
├── __init__.py
├── data_drift_detector.py         # DataDriftDetector
├── temporal_validation.py         # TemporalValidation
├── correlation_filter.py          # CorrelationFilter
└── robustness_analyzer.py        # RobustnessAnalyzer (ya existe)
```

### **src/core/optimization/**
```
src/core/optimization/
├── __init__.py
├── performance_optimizer.py       # PerformanceOptimizer, AdvancedPerformanceOptimizer
└── memory_manager.py             # Funciones de gestión de memoria
```

### **src/core/post_processing/**
```
src/core/post_processing/
├── __init__.py
├── post_analysis_processor.py     # PostAnalysisProcessor
├── visualization_preparer.py      # InteractiveVisualizationPreparer
└── export_manager.py             # Funciones de exportación
```

### **src/core/utils/**
```
src/core/utils/
├── __init__.py
├── data_utils.py                 # Funciones auxiliares de datos
├── error_handler.py              # RobustErrorHandler
├── type_converters.py            # Funciones de conversión de tipos
└── validation_utils.py           # Funciones de validación
```

---

## 🔄 **PLAN DE IMPLEMENTACIÓN**

### **FASE 1: PREPARACIÓN (Día 1)**
1. **Crear estructura de directorios**
   ```bash
   mkdir -p src/core/{analysis,config,validation,optimization,post_processing,utils}
   ```

2. **Crear archivos __init__.py**
   ```bash
   touch src/core/{analysis,config,validation,optimization,post_processing,utils}/__init__.py
   ```

3. **Backup del archivo original**
   ```bash
   cp src/core/core_engine_enhanced.py src/core/core_engine_enhanced_backup.py
   ```

### **FASE 2: EXTRACCIÓN DE UTILIDADES (Día 2)**
1. **src/core/utils/data_utils.py**
   - `_safe_sum()`
   - `_safe_values()`
   - `_improve_missing_data_handling()`
   - `safe_float()`

2. **src/core/utils/error_handler.py**
   - `RobustErrorHandler`

3. **src/core/utils/type_converters.py**
   - Funciones de conversión de tipos

### **FASE 3: EXTRACCIÓN DE CONFIGURACIÓN (Día 3)**
1. **src/core/config/kpi_config.py**
   - `KPIConfig`
   - `TradingStyleConfig`

2. **src/core/config/progress_callback.py**
   - `ProgressCallback`

3. **src/core/config/config_manager.py**
   - `ConfigManagerEnhanced`

### **FASE 4: EXTRACCIÓN DE ANÁLISIS (Días 4-6)**
1. **src/core/analysis/factor_k_analyzer.py**
   - `FactorKElite96Enhanced`
   - Funciones relacionadas con Factor K

2. **src/core/analysis/qva_analyzer.py**
   - `QVAScorerEnhanced`
   - Funciones relacionadas con QVA

3. **src/core/analysis/unified_scorer.py**
   - `UnifiedEvaluatorEnhanced`
   - Funciones de scoring unificado

4. **src/core/analysis/darwin_analyzer.py**
   - `DarwinLabsMetrics`

5. **src/core/analysis/darwin_pipeline.py**
   - `DarwinEXPipelineEnhanced`

6. **src/core/analysis/extra_kpi_manager.py**
   - `ExtraKPIManager`

### **FASE 5: EXTRACCIÓN DE VALIDACIÓN (Día 7)**
1. **src/core/validation/data_drift_detector.py**
   - `DataDriftDetector`

2. **src/core/validation/temporal_validation.py**
   - `TemporalValidation`

3. **src/core/validation/correlation_filter.py**
   - `CorrelationFilter`

### **FASE 6: EXTRACCIÓN DE OPTIMIZACIÓN (Día 8)**
1. **src/core/optimization/performance_optimizer.py**
   - `PerformanceOptimizer`
   - `AdvancedPerformanceOptimizer`

2. **src/core/optimization/memory_manager.py**
   - Funciones de gestión de memoria

### **FASE 7: EXTRACCIÓN DE POST-PROCESAMIENTO (Día 9)**
1. **src/core/post_processing/post_analysis_processor.py**
   - `PostAnalysisProcessor`

2. **src/core/post_processing/visualization_preparer.py**
   - `InteractiveVisualizationPreparer`

3. **src/core/post_processing/export_manager.py**
   - Funciones de exportación

### **FASE 8: INTEGRACIÓN Y TESTING (Día 10)**
1. **Crear nuevo core_engine_enhanced.py**
   - Importar todos los módulos
   - Mantener compatibilidad con código existente
   - Implementar Factory Pattern

2. **Tests de integración**
   - Verificar que todos los módulos funcionan
   - Validar que la GUI sigue funcionando
   - Tests de regresión

---

## 🧪 **TESTS DE VALIDACIÓN**

### **Tests Unitarios por Módulo:**
```python
# test_factor_k_analyzer.py
def test_factor_k_analyzer_creation()
def test_factor_k_calculation()
def test_factor_k_validation()

# test_qva_analyzer.py
def test_qva_analyzer_creation()
def test_qva_calculation()
def test_qva_normalization()

# test_unified_scorer.py
def test_unified_scorer_creation()
def test_unified_evaluation()
def test_score_combination()
```

### **Tests de Integración:**
```python
# test_core_integration.py
def test_all_analyzers_work_together()
def test_gui_integration_unchanged()
def test_performance_not_degraded()
def test_memory_usage_optimized()
```

---

## 🔧 **PATRONES DE DISEÑO A IMPLEMENTAR**

### **1. Factory Pattern**
```python
class AnalyzerFactory:
    @staticmethod
    def create_analyzer(analyzer_type: str, config: Dict) -> BaseAnalyzer:
        if analyzer_type == "factor_k":
            return FactorKAnalyzer(config)
        elif analyzer_type == "qva":
            return QVAAnalyzer(config)
        elif analyzer_type == "unified":
            return UnifiedScorer(config)
```

### **2. Strategy Pattern**
```python
class ScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, df: pd.DataFrame) -> pd.Series:
        pass

class FactorKStrategy(ScoringStrategy):
    def calculate_score(self, df: pd.DataFrame) -> pd.Series:
        # Implementación Factor K

class QVAStrategy(ScoringStrategy):
    def calculate_score(self, df: pd.DataFrame) -> pd.Series:
        # Implementación QVA
```

### **3. Builder Pattern**
```python
class AnalysisBuilder:
    def __init__(self):
        self.analyzers = []
        self.config = {}
    
    def add_analyzer(self, analyzer_type: str):
        self.analyzers.append(analyzer_type)
        return self
    
    def set_config(self, config: Dict):
        self.config = config
        return self
    
    def build(self) -> UnifiedEvaluator:
        return UnifiedEvaluator(self.analyzers, self.config)
```

---

## 📊 **MÉTRICAS DE ÉXITO**

### **Funcionalidad:**
- ✅ Todos los tests existentes pasan
- ✅ GUI funciona sin cambios
- ✅ Rendimiento no degradado
- ✅ Memoria optimizada

### **Arquitectura:**
- ✅ Módulos con responsabilidad única
- ✅ Imports limpios y organizados
- ✅ Patrones de diseño implementados
- ✅ Configuración centralizada

### **Mantenibilidad:**
- ✅ Código más legible
- ✅ Fácil extensión de funcionalidades
- ✅ Testing granular
- ✅ Documentación por módulo

---

## 🚨 **RIESGOS Y MITIGACIONES**

### **Riesgos Identificados:**
1. **Compatibilidad con GUI existente**
   - **Mitigación**: Mantener interfaces públicas sin cambios

2. **Rendimiento degradado**
   - **Mitigación**: Profiling antes y después

3. **Imports circulares**
   - **Mitigación**: Diseño cuidadoso de dependencias

4. **Tests fallando**
   - **Mitigación**: Tests incrementales por módulo

### **Plan de Contingencia:**
- ✅ Backup completo antes de cada fase
- ✅ Rollback automático si se detectan problemas
- ✅ Tests de regresión en cada cambio
- ✅ Documentación de cambios para reversión

---

**¿Procedemos con la Fase 1: Preparación de la estructura de directorios?** 