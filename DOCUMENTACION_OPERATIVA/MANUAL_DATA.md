# 📊 MANUAL OPERATIVO - CARPETA DATA

## 🎯 **OBJETIVO PRINCIPAL**
La carpeta `src/data/` es el **centro de gestión de datos** del sistema KVAVSKFORCERATIO. Se encarga de la ingesta, limpieza, validación y preparación de todos los datos que alimentan el análisis cuantitativo.

## 🔧 **COMPONENTES PRINCIPALES**

### **1. data_manager.py**
**Función:** Gestor central de datos
- **Carga de archivos:** CSV, Excel, PDF con validación automática
- **Limpieza de datos:** Eliminación de duplicados, conversión de tipos
- **Mapeo de columnas:** Unificación de nombres de métricas
- **Validación de integridad:** Verificación de datos faltantes y outliers

### **2. data_processing.py**
**Función:** Procesamiento avanzado de datos
- **Normalización:** Estandarización de métricas para comparación
- **Transformaciones:** Cálculo de métricas derivadas
- **Filtrado:** Eliminación de datos irrelevantes o corruptos
- **Enriquecimiento:** Añadido de metadatos y categorías

### **3. column_mapping.py**
**Función:** Sistema de mapeo inteligente de columnas
- **Reconocimiento automático:** Identifica métricas por patrones
- **Mapeo robusto:** Maneja diferentes formatos de archivos
- **Validación de esquemas:** Verifica que todas las columnas requeridas estén presentes

### **4. data_utils.py**
**Función:** Utilidades y helpers para datos
- **Conversiones:** Transformación entre formatos de datos
- **Validaciones:** Checks de calidad y consistencia
- **Optimizaciones:** Mejoras de rendimiento en procesamiento

## 🔄 **FLUJO DE TRABAJO**

### **FASE 1: INGESTA DE DATOS**
1. **Selección de archivos:** El usuario selecciona archivos CSV/Excel de estrategias
2. **Detección automática:** El sistema identifica formato y estructura
3. **Carga robusta:** Manejo de errores y formatos variados
4. **Validación inicial:** Verificación de integridad básica

### **FASE 2: LIMPIEZA Y PREPARACIÓN**
1. **Eliminación de duplicados:** Basado en nombre de estrategia
2. **Conversión de tipos:** Strings a numéricos, fechas, etc.
3. **Manejo de valores faltantes:** Imputación o eliminación según contexto
4. **Detección de outliers:** Identificación de valores anómalos

### **FASE 3: MAPEO Y NORMALIZACIÓN**
1. **Reconocimiento de columnas:** Mapeo automático de métricas
2. **Unificación de nombres:** Estandarización de nomenclatura
3. **Validación de esquemas:** Verificación de columnas requeridas
4. **Normalización de datos:** Estandarización para comparación

### **FASE 4: ENRIQUECIMIENTO**
1. **Cálculo de métricas derivadas:** Ratios, índices compuestos
2. **Categorización automática:** Clasificación por tipo de estrategia
3. **Metadatos:** Información adicional sobre origen y procesamiento
4. **Validación final:** Verificación de calidad antes del análisis

### **FASE 5: EXPORTACIÓN Y PERSISTENCIA**
1. **Formato de salida:** Preparación para análisis en core
2. **Caché inteligente:** Almacenamiento para reutilización
3. **Logging de operaciones:** Registro de transformaciones aplicadas
4. **Backup automático:** Preservación de datos originales

## 📈 **TIPOS DE DATOS MANEJADOS**

### **Datos de Estrategias**
- **Métricas de rendimiento:** CAGR, Net Profit, Profit Factor
- **Métricas de riesgo:** Max Drawdown, Sharpe Ratio, VaR
- **Métricas operativas:** Número de trades, Win Rate, Exposure
- **Métricas temporales:** Fechas de inicio, duración, frecuencia

### **Datos de Mercado**
- **Precios:** OHLCV de diferentes timeframes
- **Indicadores técnicos:** RSI, MACD, Bollinger Bands
- **Datos macro:** Volatilidad, correlaciones, regímenes
- **Eventos:** Noticias, earnings, eventos económicos

### **Datos de Portfolios**
- **Composición:** Peso de cada estrategia
- **Métricas agregadas:** Rendimiento total, riesgo conjunto
- **Correlaciones:** Matrices de correlación entre estrategias
- **Optimización:** Resultados de optimización de portfolios

## 🎨 **CARACTERÍSTICAS TÉCNICAS**

### **Robustez**
- Manejo de archivos corruptos o incompletos
- Recuperación automática de errores de carga
- Validación exhaustiva de integridad de datos
- Logging detallado de todas las operaciones

### **Flexibilidad**
- Soporte para múltiples formatos de entrada
- Configuración dinámica de mapeos
- Extensiones para nuevos tipos de datos
- APIs para integración externa

### **Rendimiento**
- Procesamiento en lotes para archivos grandes
- Optimización de memoria para datasets extensos
- Caché inteligente para operaciones repetitivas
- Paralelización de tareas independientes

## 🔍 **INTEGRACIÓN CON OTRAS CARPETAS**

### **Con CORE:**
- Proporciona datos limpios y estructurados
- Recibe configuraciones de procesamiento
- Devuelve métricas calculadas y enriquecidas

### **Con GUI:**
- Alimenta visualizaciones y tablas
- Recibe comandos de carga y procesamiento
- Proporciona feedback de progreso

### **Con ANALYSIS:**
- Suministra datos para análisis avanzados
- Recibe resultados de análisis para integración
- Facilita comparaciones y validaciones

### **Con ML:**
- Prepara datasets para entrenamiento
- Recibe predicciones para enriquecimiento
- Valida calidad de datos para ML

## 📋 **FORMATOS SOPORTADOS**

### **Entrada**
- **CSV:** Delimitador ';', decimal ',', encoding UTF-8
- **Excel:** .xlsx, .xls con múltiples hojas
- **PDF:** Tablas extraídas con pdfplumber
- **JSON:** Datos estructurados para APIs

### **Salida**
- **DataFrame:** Pandas para análisis en core
- **CSV:** Exportación limpia y estructurada
- **Excel:** Múltiples hojas con análisis
- **JSON:** Para integración con sistemas externos

## 🚀 **OPTIMIZACIONES IMPLEMENTADAS**

### **Rendimiento**
- Carga lazy de archivos grandes
- Procesamiento incremental
- Compresión de datos en caché
- Paralelización de validaciones

### **Calidad**
- Validación estadística de outliers
- Verificación de consistencia temporal
- Detección de datos duplicados
- Logging de transformaciones

### **Usabilidad**
- Mensajes de error claros y específicos
- Progreso visual de operaciones
- Configuración por archivo de configuración
- Documentación automática de cambios

## 🔧 **CONFIGURACIÓN AVANZADA**

### **Mapeos Personalizados**
- Definición de nuevos mapeos de columnas
- Configuración de validaciones específicas
- Personalización de transformaciones
- Extensiones de procesamiento

### **Validaciones Específicas**
- Rangos aceptables por métrica
- Reglas de negocio personalizadas
- Validaciones de integridad referencial
- Checks de calidad específicos

### **Optimizaciones de Rendimiento**
- Configuración de tamaños de lote
- Ajuste de parámetros de memoria
- Configuración de paralelización
- Optimización de caché

---

**💡 NOTA:** La carpeta DATA es fundamental para la calidad del análisis. Un error en la preparación de datos puede invalidar todo el análisis posterior. Siempre verificar la calidad de los datos antes de proceder al análisis. 