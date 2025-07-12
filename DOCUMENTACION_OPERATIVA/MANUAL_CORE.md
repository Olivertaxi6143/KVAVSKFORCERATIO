# 📊 MANUAL OPERATIVO - CARPETA CORE

## 🎯 **OBJETIVO PRINCIPAL**
La carpeta `src/core/` contiene el **motor central** del sistema KVAVSKFORCERATIO. Es el corazón que procesa, analiza y evalúa las estrategias de trading de forma cuantitativa y objetiva.

## 🔧 **COMPONENTES PRINCIPALES**

### **1. core_engine_enhanced.py**
**Función:** Motor principal de análisis cuantitativo
- **FactorKElite96Enhanced:** Calcula el score Factor K 9.6 con componentes S-G-E-C-T-P
- **QVAScorerEnhanced:** Evalúa rentabilidad, riesgo y consistencia
- **UnifiedEvaluatorEnhanced:** Combina Factor K + QVA en evaluación unificada
- **DarwinLabsMetrics:** Sistema predictivo para asignación de capital DarwinEX

### **2. compliance_audit.py**
**Función:** Auditoría automática de cumplimiento regulatorio
- Verifica métricas de riesgo (VaR, CVaR, Drawdown)
- Valida límites operacionales
- Genera reportes de compliance

### **3. logger_config.py**
**Función:** Sistema de logging centralizado
- Registra todas las operaciones del sistema
- Mantiene trazabilidad completa
- Facilita debugging y auditoría

## 🔄 **FLUJO DE TRABAJO**

### **FASE 1: INGESTA DE DATOS**
1. **Carga de CSV:** El sistema lee archivos de estrategias con formato europeo (delimitador ';', decimal ',')
2. **Limpieza automática:** Elimina duplicados, convierte tipos de datos, valida integridad
3. **Mapeo de columnas:** Unifica nombres de métricas usando el robust column map

### **FASE 2: ANÁLISIS CUANTITATIVO**
1. **Factor K 9.6:** Calcula componentes S (Stability), G (Growth), E (Efficiency), C (Consistency), T (Temporal), P (Predictability)
2. **QVA Score:** Evalúa rentabilidad, gestión de riesgo y consistencia operativa
3. **Score Unificado:** Combina ambos sistemas en una evaluación integral

### **FASE 3: CLASIFICACIÓN Y RANKING**
1. **Categorización automática:** Elite (≥9.2), Excellent (≥8.2), Very Good (≥7.2), Good (≥6.2), etc.
2. **Ranking por rendimiento:** Ordena estrategias según scores calculados
3. **Filtros dinámicos:** Permite filtrar por métricas específicas

### **FASE 4: ANÁLISIS AVANZADO**
1. **Detección de regímenes:** Identifica bull/bear/sideways/crisis markets
2. **Validación temporal:** Walk-forward analysis y out-of-sample testing
3. **Stress testing:** Simula condiciones extremas de mercado

### **FASE 5: REPORTES Y EXPORTACIÓN**
1. **Reportes ejecutivos:** Resúmenes con métricas clave
2. **Exportación Excel:** Múltiples hojas con análisis detallado
3. **Dashboards HTML:** Visualizaciones interactivas

## 📈 **MÉTRICAS CALCULADAS**

### **Métricas de Rentabilidad**
- **CAGR:** Crecimiento anual compuesto
- **Net Profit:** Beneficio neto total
- **Profit Factor:** Ratio de ganancias vs pérdidas
- **Win Rate:** Porcentaje de operaciones ganadoras

### **Métricas de Riesgo**
- **Max Drawdown:** Pérdida máxima desde pico
- **Sharpe Ratio:** Rentabilidad ajustada por riesgo
- **Sortino Ratio:** Versión mejorada del Sharpe
- **VaR (95%):** Valor en Riesgo al 95% de confianza
- **CVaR (95%):** Valor en Riesgo Condicional

### **Métricas de Consistencia**
- **Calmar Ratio:** CAGR / Max Drawdown
- **Recovery Factor:** Net Profit / Max Drawdown
- **SQN Score:** System Quality Number
- **Expectancy:** Esperanza matemática por operación

## 🎨 **CARACTERÍSTICAS TÉCNICAS**

### **Robustez**
- Manejo automático de errores y datos faltantes
- Validación exhaustiva de inputs
- Recuperación automática de fallos

### **Escalabilidad**
- Procesamiento en hilos para grandes volúmenes
- Optimización de memoria para datasets extensos
- Caché inteligente para cálculos repetitivos

### **Precisión**
- Cálculos con precisión numérica alta
- Validación estadística de resultados
- Comparación con benchmarks establecidos

## 🔍 **INTEGRACIÓN CON OTRAS CARPETAS**

### **Con DATA:**
- Recibe datos limpios y estructurados
- Devuelve análisis procesados

### **Con GUI:**
- Proporciona resultados para visualización
- Recibe comandos de usuario para análisis

### **Con ANALYSIS:**
- Alimenta análisis avanzados y científicos
- Recibe configuraciones de análisis específicos

### **Con ML:**
- Proporciona datos para entrenamiento de modelos
- Recibe predicciones para integración en scoring

## 📋 **CONFIGURACIÓN Y PERSONALIZACIÓN**

### **Parámetros Ajustables**
- Pesos de componentes del Factor K
- Umbrales de categorización
- Configuración de regímenes de mercado
- Parámetros de validación temporal

### **Extensiones Disponibles**
- Nuevos algoritmos de scoring
- Métricas personalizadas
- Integración con APIs externas
- Conectores con bases de datos

## 🚀 **OPTIMIZACIONES IMPLEMENTADAS**

### **Rendimiento**
- Vectorización de cálculos con NumPy
- Paralelización de procesos pesados
- Optimización de memoria con pandas

### **Precisión**
- Validación estadística de resultados
- Comparación con benchmarks
- Tests unitarios exhaustivos

### **Usabilidad**
- Logging detallado para debugging
- Manejo robusto de errores
- Documentación completa de APIs

---

**💡 NOTA:** El core es el componente más crítico del sistema. Cualquier modificación debe ser probada exhaustivamente y documentada para mantener la integridad del análisis cuantitativo. 