# Guía de Usuario - QVA Strategy Studio

## 📋 Resumen Ejecutivo

QVA Strategy Studio es una aplicación profesional para el análisis cuantitativo de estrategias de trading. Esta guía proporciona instrucciones detalladas para utilizar todas las funcionalidades del sistema.

## 🚀 Instalación y Configuración

### Requisitos del Sistema
- **Python**: 3.11 o superior
- **Sistema Operativo**: Windows 10/11, macOS 10.15+, Linux
- **Memoria RAM**: Mínimo 4GB, recomendado 8GB
- **Espacio en Disco**: 500MB disponibles

### Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/usuario/qva-strategy-studio.git
   cd qva-strategy-studio
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**:
   ```bash
   python run_gui.py
   ```

## 🎯 Funcionalidades Principales

### 1. Carga de Datos

#### Cargar Estrategias CSV
1. Hacer clic en **"📁 Cargar Datos"** en la barra de herramientas
2. Seleccionar archivo CSV con datos de estrategias
3. El sistema validará automáticamente el formato
4. Se mostrarán estadísticas de carga en la barra de estado

**Formato CSV Requerido**:
- Delimitador: `;` (punto y coma)
- Decimal: `,` (coma)
- Columnas obligatorias: `Strategy_Name`, `Factor_K`, `CAGR_IS`, `Sharpe_Ratio_IS`, `Max_Drawdown_IS`

#### Cargar Portafolios PDF
1. Hacer clic en **"📁 Importar Portafolios PDF"**
2. Seleccionar archivos PDF de portafolios
3. El sistema extraerá automáticamente las tablas
4. Se alinearán las métricas con el formato del CSV

### 2. Análisis Científico

#### Pipeline DarwinEX
1. Ir a la pestaña **"🧪 Análisis Científico"**
2. Hacer clic en **"Ejecutar Pipeline DarwinEX"**
3. El sistema aplicará 6 filtros automáticamente:
   - **Gold Access** (D-Score ≥ 70)
   - **Track Record** (≥ 8 meses)
   - **LEA/OS Positive** (Corta pérdidas, deja correr ganancias)
   - **Correlation 6m** (≤ 0.25 vs índices)
   - **Discipline** (Estabilidad de frecuencia)
   - **DD Correlation** (< 0.6 con drawdowns)

#### Visualización de Resultados
- **Estadísticas generales**: Total, aprobadas, rechazadas, tasa de éxito
- **Distribución de tickets**: Gold, Silver, Bronze
- **Top 5 estrategias**: Con scores y tickets
- **Alertas de riesgo**: Identificadas automáticamente

### 3. Filtros Avanzados

#### Filtros Rápidos
En el panel izquierdo:
- **Factor K mínimo**: Deslizar para establecer umbral
- **Sharpe Ratio mínimo**: Deslizar para establecer umbral
- **Drawdown máximo**: Deslizar para establecer umbral

#### Filtros Avanzados
1. Hacer clic en **"🔍 Filtros Avanzados"**
2. Configurar rangos para cada métrica
3. Aplicar filtros de categoría
4. Revisar resultados filtrados
5. Guardar configuración de filtros

### 4. Interpretación de Métricas

#### Factor K Elite 9.6
- **🥇 Elite (≥9.2)**: Estrategias excepcionales
- **🥈 Excellent (≥8.2)**: Estrategias muy buenas
- **🥉 Very Good (≥7.2)**: Estrategias buenas
- **⭐ Good (≥6.2)**: Estrategias aceptables
- **⚠️ Poor (≥3.1)**: Estrategias con problemas
- **❌ Very Poor (<3.1)**: Estrategias no recomendadas

#### Predictibilidad
- **🎯 Excelente (≥85%)**: Alta confiabilidad
- **🎯 Buena (70-84%)**: Buena estabilidad
- **🎯 Aceptable (60-69%)**: Estabilidad moderada
- **🎯 Baja (<60%)**: Alto riesgo

#### Sharpe Ratio
- **≥2.0**: Excelente rendimiento
- **1.5-2.0**: Muy bueno
- **1.0-1.5**: Bueno
- **0.5-1.0**: Aceptable
- **<0.5**: Pobre

#### Máximo Drawdown
- **<10%**: Excelente (bajo riesgo)
- **10-20%**: Bueno
- **20-30%**: Aceptable
- **30-50%**: Alto riesgo
- **>50%**: Muy alto riesgo

### 5. Tooltips Informativos

#### Uso de Tooltips
- **Pasar el mouse** sobre cualquier métrica para ver información detallada
- **Tooltips automáticos** aparecen después de 2 segundos
- **Información contextual** según la métrica seleccionada

#### Contenido de Tooltips
- **Factor K**: Componentes, categorías, pesos por régimen
- **Predictibilidad**: Escalas, factores, recomendaciones
- **Sharpe Ratio**: Interpretación, fórmula, importancia
- **Drawdown**: Interpretación, importancia, recuperación
- **CAGR**: Interpretación, fórmula, consideraciones

### 6. Panel de Ayuda Contextual

#### Acceso al Panel
1. Hacer clic en **"❓ Ayuda"** en el menú
2. Se abrirá el panel de ayuda con 4 secciones

#### Secciones Disponibles

**📊 Métricas y KPIs**
- Explicación detallada de cada métrica
- Fórmulas y cálculos
- Interpretación profesional

**🔍 Guías de Interpretación**
- Sistema de badges visuales
- Fila sticky y criterios
- Esquema de colores

**📚 Tutoriales Paso a Paso**
- Carga de datos
- Filtros avanzados
- Análisis científico
- Exportación

**❓ Preguntas Frecuentes**
- Cómo identificar la mejor estrategia
- Interpretación de predictibilidad
- Filtros más eficientes
- Exportación de resultados
- Optimización de rendimiento

### 7. Guías de Interpretación Automática

#### Interpretación Automática
El sistema interpreta automáticamente cada estrategia y proporciona:
- **Categorización visual** con badges y colores
- **Recomendaciones contextuales** basadas en métricas
- **Score general** calculado con pesos optimizados
- **Recomendación general** para la estrategia

#### Score General
Calculado con los siguientes pesos:
- **Factor K**: 35%
- **Predictibilidad**: 25%
- **Sharpe Ratio**: 20%
- **Drawdown**: 15%
- **CAGR**: 5%

#### Recomendaciones Automáticas
- **🏆 ESTRATEGIA EXCEPCIONAL**: Múltiples métricas excelentes
- **🥈 ESTRATEGIA MUY BUENA**: Mayoría de métricas excelentes o buenas
- **🥉 ESTRATEGIA BUENA**: Buen balance de métricas
- **⭐ ESTRATEGIA ACEPTABLE**: Métricas moderadas
- **⚠️ ESTRATEGIA CON RIESGO**: Múltiples métricas pobres
- **❓ ESTRATEGIA MIXTA**: Métricas variadas

### 8. Fila Sticky

#### Funcionalidad
- **Mejor estrategia** se mantiene visible en la parte superior
- **Criterios de selección**:
  - Factor K más alto (prioridad principal)
  - Predictibilidad excelente (≥85%)
  - Sharpe Ratio superior (≥2.0)
  - Drawdown bajo (<10%)

#### Características Visuales
- **Fondo destacado** con color diferente
- **Borde especial** más grueso
- **Icono de estrella** ⭐ para indicar mejor estrategia
- **Tooltip informativo** explicando la selección

### 9. Exportación Avanzada

#### Exportación Excel
1. Hacer clic en **"📤 Exportación Avanzada"**
2. Seleccionar **"Excel"** como formato
3. Se generarán 7 hojas automáticamente:
   - **Ranking**: Estrategias ordenadas por Factor K
   - **Por Régimen**: Análisis por régimen de mercado
   - **Componentes FK96**: Desglose de componentes del Factor K
   - **Métricas Derivadas**: Métricas calculadas adicionales
   - **IS-OOS**: Análisis In-Sample vs Out-of-Sample
   - **Categorías**: Distribución por categorías
   - **Datos Completos**: Todos los datos sin procesar

#### Exportación HTML
1. Seleccionar **"HTML"** como formato
2. Se generará un dashboard interactivo con:
   - Gráficos de Factor K
   - Scatter plots de CAGR vs Sharpe
   - Distribución por categorías
   - Top 10 estrategias

#### Exportación .SQX
1. Hacer clic en **"📁 Exportar .SQX"**
2. Seleccionar directorio de salida
3. Se exportarán archivos .sqx para las estrategias seleccionadas

## 🎨 Interfaz de Usuario

### Barra de Herramientas
- **📁 Cargar Datos**: Cargar archivos CSV
- **🔍 Filtros Avanzados**: Configurar filtros
- **📊 Gráficos Interactivos**: Visualizar datos
- **⚖️ Comparar Estrategias**: Comparar seleccionadas
- **📤 Exportación Avanzada**: Exportar resultados
- **🧪 Análisis Científico**: Ejecutar análisis
- **📈 Tail Risk Analysis**: Análisis de riesgo
- **🎯 AXISelect Analysis**: Análisis de selección
- **❓ Ayuda**: Abrir panel de ayuda

### Panel Izquierdo
- **📋 Navegación**: Pasos del análisis
- **Filtros Rápidos**: Controles deslizantes
- **Estadísticas**: Resumen de datos cargados

### Panel Central
- **Tabla de Datos**: Estrategias con métricas
- **Fila Sticky**: Mejor estrategia destacada
- **Badges Visuales**: Categorización automática
- **Colores Automáticos**: Codificación por calidad

### Panel Derecho
- **Detalles de Estrategia**: Información seleccionada
- **Gráficos**: Visualizaciones específicas
- **Controles**: Opciones adicionales

## 🔧 Configuración Avanzada

### Personalización de Criterios
```python
# Criterios personalizables para fila sticky
STICKY_CRITERIA = {
    "factor_k_weight": 0.35,
    "predictability_weight": 0.25,
    "sharpe_weight": 0.20,
    "drawdown_weight": 0.15,
    "cagr_weight": 0.05
}
```

### Configuración de Badges
```python
# Configuración de badges
BADGE_CONFIG = {
    "show_badges": True,
    "badge_size": "medium",
    "badge_position": "left",
    "show_tooltips": True
}
```

### Configuración de Fila Sticky
```python
# Configuración de fila sticky
STICKY_CONFIG = {
    "enabled": True,
    "highlight_color": "#E6F3FF",
    "border_style": "solid",
    "border_width": 2,
    "show_indicator": True
}
```

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error al Cargar Datos
**Síntomas**: Mensaje de error al cargar CSV
**Solución**:
- Verificar formato del archivo (delimitador `;`, decimal `,`)
- Comprobar que las columnas obligatorias estén presentes
- Revisar que no haya caracteres especiales en los datos

#### 2. Badges No Se Muestran
**Síntomas**: No aparecen badges en la tabla
**Solución**:
- Verificar configuración `show_badges: True`
- Comprobar que los datos tengan valores válidos
- Reiniciar la aplicación

#### 3. Fila Sticky No Funciona
**Síntomas**: No se destaca la mejor estrategia
**Solución**:
- Verificar que haya datos cargados
- Comprobar criterios de selección
- Revisar configuración de tabla

#### 4. Tooltips No Aparecen
**Síntomas**: No se muestran tooltips al pasar el mouse
**Solución**:
- Verificar configuración `show_tooltips: True`
- Comprobar que el mouse esté sobre la métrica
- Esperar 2 segundos para que aparezca

#### 5. Error en Análisis Científico
**Síntomas**: Error al ejecutar pipeline DarwinEX
**Solución**:
- Verificar que haya datos cargados
- Comprobar que las columnas requeridas estén presentes
- Revisar logs de error en la consola

### Logs de Debug

#### Habilitar Logs Detallados
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Verificar Estado del Sistema
```python
# En la consola de Python
from src.gui.main_window import MainWindow
app = MainWindow()
app.debug_system_status()
```

## 📊 Métricas de Rendimiento

### Tiempos de Respuesta Esperados
- **Carga de datos**: <5 segundos para 1000 estrategias
- **Aplicación de filtros**: <1 segundo
- **Análisis científico**: <30 segundos
- **Exportación Excel**: <10 segundos
- **Exportación HTML**: <15 segundos

### Uso de Recursos
- **Memoria RAM**: <500MB para datasets normales
- **CPU**: <20% durante operaciones normales
- **Disco**: <100MB para archivos temporales

## 🔄 Actualizaciones

### Versión Actual
- **Versión**: 2.0
- **Fecha**: 2025-01-15
- **Nuevas Funcionalidades**:
  - Tooltips informativos
  - Panel de ayuda contextual
  - Guías de interpretación automática
  - Sistema de badges visuales
  - Fila sticky mejorada

### Próximas Actualizaciones
- **Versión 2.1**: Badges dinámicos
- **Versión 2.2**: Filtros visuales
- **Versión 2.3**: Temas personalizables
- **Versión 2.4**: Animaciones y transiciones

## 📞 Soporte

### Contacto
- **Email**: soporte@qvastrategystudio.com
- **Documentación**: https://docs.qvastrategystudio.com
- **GitHub**: https://github.com/usuario/qva-strategy-studio

### Reportar Problemas
1. Revisar esta guía de troubleshooting
2. Verificar logs de error
3. Crear issue en GitHub con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs de error
   - Configuración del sistema

---

**Última actualización**: 2025-01-15  
**Versión**: 2.0  
**Autor**: QVA Strategy Studio Development Team 