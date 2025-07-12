# 👤 GUÍA DE USUARIO - KFORCEVSQVARATIOS v2.0

## 🎯 Introducción

**KFORCEVSQVARATIOS v2.0** es un sistema avanzado de análisis y ranking de estrategias de trading diseñado para profesionales que requieren máxima precisión y robustez en la evaluación de estrategias.

### Características Principales
- ✅ **Análisis Científico**: Métricas científicas avanzadas para evaluación precisa
- ✅ **Asesor Inteligente**: Análisis automático con recomendaciones personalizadas
- ✅ **Interfaz Intuitiva**: GUI moderna y fácil de usar
- ✅ **Validación Robusta**: Sistema de validación automática de datos
- ✅ **Exportación Flexible**: Múltiples formatos de exportación

---

## 🚀 Primeros Pasos

### 1. Iniciar el Sistema

#### 1.1 Ejecución Básica
```bash
# Ejecutar desde línea de comandos
python src/gui_enhanced_rank.py
```

#### 1.2 Verificar Inicialización
- ✅ Ventana principal se abre correctamente
- ✅ Título: "KFORCEVSQVARATIOS v2.0 - Ranking Robusto con DataManager"
- ✅ Tamaño: 1200x800 píxeles
- ✅ Componentes visibles: botones, campos de entrada, pestañas

### 2. Preparar Datos

#### 2.1 Estructura de Archivos Requerida
```
📁 Directorio de Datos/
├── 📄 DatabankExport_M1.csv    # Archivo de KPIs de estrategias
└── 📄 DATOSMQL5.csv            # Archivo de datos de mercado
```

#### 2.2 Formato del Archivo de KPIs
```csv
Strategy_Name,timeframe,total_data_months,#_of_trades,net_profit_is,net_profit_oos,
sharpe_ratio_is,sharpe_ratio_oos,profit_factor_is,profit_factor_oos,
max_drawdown_is,max_drawdown_oos,cagr_is,cagr_oos,winning_percent_is,
winning_percent_oos,calmarratio_is,calmarratio_oos
```

#### 2.3 Formato del Archivo de Mercado
```csv
Date,Open,High,Low,Close,Volume
```

---

## 📊 Flujo de Trabajo Básico

### Paso 1: Cargar Datos

#### 1.1 Seleccionar Archivos
1. **Hacer clic** en "Cargar Archivos"
2. **Navegar** al directorio con los archivos de datos
3. **Seleccionar** `DatabankExport_M1.csv` (KPIs)
4. **Seleccionar** `DATOSMQL5.csv` (datos de mercado)
5. **Confirmar** la carga

#### 1.2 Verificar Carga
- ✅ Mensaje: "Archivos cargados correctamente"
- ✅ Contador de estrategias visible
- ✅ Información de datos mostrada en la interfaz

### Paso 2: Configurar Análisis

#### 2.1 Estilo de Trading
- **CONSERVADOR**: Preservación de capital (recomendado para principiantes)
- **MODERADO**: Balance riesgo/retorno (recomendado para intermedios)
- **AGRESIVO**: Maximización de retornos (solo para expertos)

#### 2.2 Parámetros de Análisis
- **Percentil**: 20 (recomendado) - Filtra las mejores estrategias
- **Top N**: 10 (recomendado) - Número de estrategias a seleccionar
- **KPIs Seleccionados**: 5 (recomendado) - Métricas principales

#### 2.3 Configuración Avanzada
- **Métricas Científicas**: Habilitado (recomendado)
- **Validación Estricta**: Habilitado (recomendado)
- **Cache**: Habilitado (mejora rendimiento)

### Paso 3: Ejecutar Análisis

#### 3.1 Iniciar Proceso
1. **Hacer clic** en "Ejecutar Análisis"
2. **Esperar** el procesamiento (2-3 minutos típicamente)
3. **Verificar** progreso en la barra de estado

#### 3.2 Verificar Resultados
- ✅ Mensaje: "Análisis completado exitosamente"
- ✅ Tabla de resultados visible
- ✅ Métricas calculadas mostradas
- ✅ Categorías de calidad asignadas

### Paso 4: Revisar Resultados

#### 4.1 Tabla Principal
- **Estrategias ordenadas** por score científico
- **Métricas detalladas** para cada estrategia
- **Categorías de calidad** (Excelente, Muy Bueno, Bueno, etc.)

#### 4.2 Información de Métricas
- **Unified_Score_Scientific**: Score principal de evaluación
- **IS_OOS_Predictivity**: Capacidad predictiva
- **Temporal_Stability**: Estabilidad temporal
- **Métricas tradicionales**: Sharpe, Profit Factor, etc.

### Paso 5: Transferir al Asesor

#### 5.1 Seleccionar Estrategias
1. **Revisar** resultados del análisis
2. **Identificar** estrategias de interés
3. **Seleccionar** estrategias deseadas
4. **Hacer clic** en "Transferir al Asesor"

#### 5.2 Verificar Transferencia
- ✅ Mensaje: "Estrategias transferidas al asesor"
- ✅ Pestañas del asesor disponibles
- ✅ Análisis detallado visible

---

## 🧠 Uso del Asesor Financiero

### Pestaña Científica

#### Información Disponible
- **Métricas Científicas Detalladas**
  - Unified_Score_Scientific
  - IS_OOS_Predictivity
  - Temporal_Stability
  - Análisis de predictibilidad

#### Interpretación
- **Score > 0.8**: Excelente calidad científica
- **Score 0.6-0.8**: Muy buena calidad científica
- **Score 0.4-0.6**: Buena calidad científica
- **Score < 0.4**: Calidad científica limitada

### Pestaña Empírica

#### Información Disponible
- **Estadísticas Empíricas**
  - Sharpe Ratio (IS/OOS)
  - Profit Factor (IS/OOS)
  - Maximum Drawdown (IS/OOS)
  - CAGR (IS/OOS)
  - Winning Percentage (IS/OOS)
  - Calmar Ratio (IS/OOS)

#### Interpretación
- **Sharpe > 1.5**: Excelente retorno ajustado por riesgo
- **Profit Factor > 2.0**: Excelente ratio de ganancias
- **Max Drawdown < 10%**: Riesgo controlado
- **CAGR > 15%**: Excelente crecimiento anual

### Pestaña de Estrategias Seleccionadas

#### Funcionalidades
- **Lista Detallada** de estrategias seleccionadas
- **Métricas Individuales** por estrategia
- **Opciones de Exportación**
- **Análisis Comparativo**

#### Acciones Disponibles
- **Exportar Resultados**: Guardar análisis en CSV/Excel
- **Ver Detalles**: Hacer doble clic para detalles completos
- **Comparar Estrategias**: Análisis comparativo
- **Generar Reporte**: Reporte completo en PDF

---

## 📈 Casos de Uso Avanzados

### Caso 1: Análisis Conservador

#### Objetivo
Preservar capital mientras se obtienen retornos moderados.

#### Configuración
```python
style = "CONSERVADOR"
percentil = 10  # Solo las mejores 10%
top_n = 5       # Seleccionar solo 5 estrategias
```

#### Interpretación de Resultados
- **Enfoque**: Estrategias con bajo drawdown
- **Prioridad**: Sharpe Ratio y Calmar Ratio
- **Riesgo**: Máximo drawdown < 15%

### Caso 2: Análisis Agresivo

#### Objetivo
Maximizar retornos asumiendo mayor riesgo.

#### Configuración
```python
style = "AGRESIVO"
percentil = 30  # Top 30% de estrategias
top_n = 15      # Seleccionar 15 estrategias
```

#### Interpretación de Resultados
- **Enfoque**: Estrategias con alto retorno
- **Prioridad**: CAGR y Profit Factor
- **Riesgo**: Drawdown aceptable hasta 25%

### Caso 3: Análisis de Diversificación

#### Objetivo
Crear un portafolio diversificado de estrategias.

#### Configuración
```python
style = "MODERADO"
percentil = 20
top_n = 10
# Habilitar análisis de correlación
```

#### Interpretación de Resultados
- **Correlación Baja**: < 0.3 entre estrategias
- **Diversificación Efectiva**: > 0.7
- **Riesgo de Concentración**: < 0.2

---

## 🔧 Configuración Avanzada

### Configuración de Rendimiento

#### Optimizar Memoria
```python
# En config_produccion.py
BATCH_SIZE = 50  # Reducir para menor uso de memoria
MAX_MEMORY_USAGE = 512  # MB
```

#### Optimizar Velocidad
```python
# Habilitar cache
ENABLE_CACHE = True
CACHE_EXPIRY = 3600  # 1 hora

# Habilitar procesamiento paralelo
ENABLE_PARALLEL_PROCESSING = True
```

### Configuración de Validación

#### Validación Estricta
```python
STRICT_VALIDATION = True
ALLOW_MISSING_VALUES = False
MAX_DRAWDOWN_THRESHOLD = 0.15
MIN_SHARPE_RATIO = 0.5
```

#### Validación Flexible
```python
STRICT_VALIDATION = False
ALLOW_MISSING_VALUES = True
MAX_DRAWDOWN_THRESHOLD = 0.25
MIN_SHARPE_RATIO = 0.0
```

### Configuración de Logging

#### Logging Detallado
```python
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

#### Logging de Producción
```python
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
```

---

## 📊 Interpretación de Métricas

### Métricas Científicas

#### Unified_Score_Scientific
- **Rango**: 0.0 - 1.0
- **Excelente**: > 0.8
- **Muy Bueno**: 0.6 - 0.8
- **Bueno**: 0.4 - 0.6
- **Regular**: 0.2 - 0.4
- **Pobre**: < 0.2

#### IS_OOS_Predictivity
- **Rango**: 0.0 - 1.0
- **Excelente**: > 0.7 (alta predictibilidad)
- **Bueno**: 0.5 - 0.7
- **Regular**: 0.3 - 0.5
- **Pobre**: < 0.3 (baja predictibilidad)

#### Temporal_Stability
- **Rango**: 0.0 - 1.0
- **Excelente**: > 0.8 (muy estable)
- **Bueno**: 0.6 - 0.8
- **Regular**: 0.4 - 0.6
- **Pobre**: < 0.4 (inestable)

### Métricas Empíricas

#### Sharpe Ratio
- **Excelente**: > 1.5
- **Muy Bueno**: 1.0 - 1.5
- **Bueno**: 0.5 - 1.0
- **Regular**: 0.0 - 0.5
- **Pobre**: < 0.0

#### Profit Factor
- **Excelente**: > 2.0
- **Muy Bueno**: 1.5 - 2.0
- **Bueno**: 1.2 - 1.5
- **Regular**: 1.0 - 1.2
- **Pobre**: < 1.0

#### Maximum Drawdown
- **Excelente**: < 5%
- **Muy Bueno**: 5% - 10%
- **Bueno**: 10% - 15%
- **Regular**: 15% - 20%
- **Pobre**: > 20%

#### CAGR (Compound Annual Growth Rate)
- **Excelente**: > 20%
- **Muy Bueno**: 15% - 20%
- **Bueno**: 10% - 15%
- **Regular**: 5% - 10%
- **Pobre**: < 5%

---

## 🟢 Nota importante sobre Drawdown (actualización 2025-07-12)

- El sistema utiliza exclusivamente la columna **'Max DD %'** (porcentaje, admite formato europeo con coma decimal) para todos los análisis de drawdown, tanto en los módulos Darwinex como Axi Select.
- No se debe usar la columna 'Drawdown' (valores monetarios) para análisis de riesgo ni scoring.
- Los umbrales de interpretación son:
    - **Axi Select**: 10% para cuarentena
    - **Darwinex**: 20% para correlación DD
- El sistema convierte automáticamente el formato y valida los valores para evitar errores de interpretación.

---

## 🔍 Solución de Problemas

### Problema: "Error al cargar archivos"

#### Causas Comunes
1. **Formato incorrecto**: Verificar estructura CSV
2. **Columnas faltantes**: Verificar nombres de columnas
3. **Datos corruptos**: Verificar integridad del archivo
4. **Permisos**: Verificar permisos de lectura

#### Soluciones
```bash
# Verificar formato del archivo
head -5 DatabankExport_M1.csv

# Verificar columnas requeridas
python -c "
import pandas as pd
df = pd.read_csv('DatabankExport_M1.csv')
print('Columnas disponibles:', df.columns.tolist())
"
```

### Problema: "Análisis no completa"

#### Causas Comunes
1. **Memoria insuficiente**: Reducir batch_size
2. **Timeout**: Aumentar timeout_analysis
3. **Datos muy grandes**: Procesar en lotes
4. **Error en datos**: Verificar integridad

#### Soluciones
```python
# Reducir uso de memoria
BATCH_SIZE = 25  # Reducir de 100 a 25

# Aumentar timeout
TIMEOUT_ANALYSIS = 600  # 10 minutos

# Habilitar procesamiento por lotes
ENABLE_BATCH_PROCESSING = True
```

### Problema: "Resultados no aparecen"

#### Causas Comunes
1. **Filtros muy estrictos**: Ajustar percentil
2. **Datos insuficientes**: Verificar cantidad de datos
3. **Validación fallida**: Revisar logs de error
4. **Configuración incorrecta**: Verificar parámetros

#### Soluciones
```python
# Ajustar filtros
percentil = 50  # Aumentar de 20 a 50
top_n = 20      # Aumentar de 10 a 20

# Verificar datos
print(f"Estrategias disponibles: {len(df)}")
print(f"Estrategias después de filtro: {len(df_filtered)}")
```

---

## 📝 Mejores Prácticas

### 1. Preparación de Datos
- ✅ **Validar formato**: Verificar estructura CSV antes de cargar
- ✅ **Limpiar datos**: Eliminar valores extremos o corruptos
- ✅ **Verificar integridad**: Asegurar que no hay datos faltantes críticos
- ✅ **Documentar origen**: Mantener registro del origen de los datos

### 2. Configuración de Análisis
- ✅ **Comenzar conservador**: Usar configuración conservadora inicialmente
- ✅ **Ajustar gradualmente**: Modificar parámetros basado en resultados
- ✅ **Documentar cambios**: Mantener registro de configuraciones usadas
- ✅ **Validar resultados**: Verificar que los resultados tienen sentido

### 3. Interpretación de Resultados
- ✅ **Revisar múltiples métricas**: No basarse solo en una métrica
- ✅ **Considerar contexto**: Evaluar resultados en contexto del mercado
- ✅ **Validar con datos históricos**: Comparar con análisis previos
- ✅ **Documentar decisiones**: Mantener registro de decisiones tomadas

### 4. Uso del Asesor
- ✅ **Revisar todas las pestañas**: No ignorar ninguna sección
- ✅ **Considerar recomendaciones**: Evaluar sugerencias del asesor
- ✅ **Exportar resultados**: Guardar análisis importantes
- ✅ **Actualizar regularmente**: Revisar análisis periódicamente

---

## 📞 Soporte y Recursos

### Documentación Adicional
- **Documentación Técnica**: `DOCUMENTACION_FLUJO_TRABAJO.md`
- **Guía de Instalación**: `GUIA_INSTALACION.md`
- **Roadmap del Proyecto**: `ROADMAP_PROGRESO.md`

### Recursos de Aprendizaje
- **Tutoriales**: Disponibles en la documentación
- **Casos de Uso**: Ejemplos prácticos incluidos
- **Videos**: Tutoriales en video (si están disponibles)

### Soporte Técnico
- **Email**: soporte@kforcevsqvaratios.com
- **Documentación**: [URL_DOCUMENTACION]
- **Issues**: [URL_GITHUB_ISSUES]
- **FAQ**: Preguntas frecuentes en la documentación

---

## ✅ Checklist de Uso

### Configuración Inicial
- [ ] Sistema instalado correctamente
- [ ] Datos preparados en formato correcto
- [ ] Configuración inicial aplicada
- [ ] Test de funcionamiento ejecutado

### Análisis Básico
- [ ] Datos cargados exitosamente
- [ ] Configuración de análisis aplicada
- [ ] Análisis ejecutado sin errores
- [ ] Resultados revisados e interpretados
- [ ] Estrategias seleccionadas para asesor

### Uso del Asesor
- [ ] Pestaña científica revisada
- [ ] Pestaña empírica revisada
- [ ] Pestaña de estrategias seleccionadas revisada
- [ ] Recomendaciones consideradas
- [ ] Resultados exportados (si es necesario)

### Configuración Avanzada
- [ ] Configuración de rendimiento optimizada
- [ ] Configuración de validación ajustada
- [ ] Logging configurado apropiadamente
- [ ] Backup de configuración creado

---

*Guía de usuario v2.0 - KFORCEVSQVARATIOS*
*Fecha: 2025-07-11* 