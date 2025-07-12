# Módulo GUI Enhancements

## Descripción
Módulo de interfaz gráfica de usuario (GUI) para QVA Strategy Studio. Permite la interacción visual, importación de estrategias, visualización de métricas y exportación de resultados.

## Componentes

### gui_enhanced_rank.py
- Interfaz principal para el rankeo de estrategias
- Integración con el motor core para análisis
- Visualización de métricas clave (Factor K, CAGR, Sharpe, DD, etc.)
- Coloreado automático de filas por categoría
- Filtros avanzados y paneles dockables
- Exportación a Excel y HTML

### scientific_gui_tab.py
- Pestaña de análisis científico
- Visualización de histogramas, scatter plots y gráficos de barras
- Integración con matplotlib y plotly
- Generación de dashboards interactivos

## Funcionalidades Principales

### Importación de Estrategias
- Diálogo para cargar archivos CSV
- Limpieza y mapeo de columnas
- Validación de datos importados

### Visualización y Filtros
- Tabla central con QTableView y QSortFilterProxyModel
- Filtros numéricos y por categoría
- Tooltips y atajos de teclado

### Dashboards y Gráficos
- Histograma de Factor K
- Barras de estrategias por categoría
- Scatter CAGR IS/OOS
- Pie de distribución por régimen

### Exportación
- Exportación avanzada a Excel (openpyxl)
- Exportación de dashboards a HTML (plotly)

## Uso

```python
from src.gui.gui_enhanced_rank import EnhancedRankGUI

gui = EnhancedRankGUI()
gui.show()
```

## Dependencias
- PySide6
- matplotlib
- plotly
- pandas
- numpy
- openpyxl

## Tests
- Validación de carga de estrategias
- Tests de visualización de métricas
- Verificación de exportación a Excel/HTML 