"""
Funciones de Visualización de Datos
===================================

Funciones comunes para visualización de datos utilizadas
por múltiples módulos de análisis.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
import warnings

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

def create_correlation_heatmap(correlation_data: Dict[str, float], 
                             title: str = "Correlation Matrix") -> Dict[str, Any]:
    """
    Crea datos para un heatmap de correlación.
    
    Args:
        correlation_data: Diccionario con correlaciones
        title: Título del gráfico
        
    Returns:
        Diccionario con datos para visualización
    """
    try:
        # Crear matriz de correlación
        if correlation_data:
            # Extraer nombres de variables
            variables = list(correlation_data.keys())
            n_vars = len(variables)
            
            # Crear matriz de correlación
            corr_matrix = np.zeros((n_vars, n_vars))
            
            for i, var1 in enumerate(variables):
                for j, var2 in enumerate(variables):
                    if var1 == var2:
                        corr_matrix[i, j] = 1.0
                    else:
                        # Buscar correlación en los datos
                        key = f"{var1}_vs_{var2}"
                        if key in correlation_data:
                            corr_matrix[i, j] = correlation_data[key]
                        else:
                            corr_matrix[i, j] = 0.0
            
            visualization_data = {
                "type": "correlation_heatmap",
                "title": title,
                "data": corr_matrix.tolist(),
                "variables": variables,
                "correlation_data": correlation_data
            }
        else:
            visualization_data = {
                "type": "correlation_heatmap",
                "title": title,
                "data": [],
                "variables": [],
                "correlation_data": {},
                "error": "No hay datos de correlación"
            }
        
        logger.info("✅ Datos de heatmap de correlación creados")
        return visualization_data
        
    except Exception as e:
        logger.error(f"❌ Error creando heatmap de correlación: {e}")
        return {"error": str(e), "type": "correlation_heatmap"}

def create_distribution_plot(data: pd.Series, 
                           title: str = "Distribution Plot") -> Dict[str, Any]:
    """
    Crea datos para un gráfico de distribución.
    
    Args:
        data: Serie de datos
        title: Título del gráfico
        
    Returns:
        Diccionario con datos para visualización
    """
    try:
        # Calcular estadísticas de distribución
        stats = {
            "mean": float(data.mean()),
            "median": float(data.median()),
            "std": float(data.std()),
            "min": float(data.min()),
            "max": float(data.max()),
            "count": len(data),
            "skewness": float(data.skew()),
            "kurtosis": float(data.kurtosis())
        }
        
        # Crear histograma
        hist_data, bin_edges = np.histogram(data.dropna(), bins=20)
        
        visualization_data = {
            "type": "distribution_plot",
            "title": title,
            "data": data.tolist(),
            "histogram": {
                "counts": hist_data.tolist(),
                "bin_edges": bin_edges.tolist()
            },
            "statistics": stats
        }
        
        logger.info("✅ Datos de gráfico de distribución creados")
        return visualization_data
        
    except Exception as e:
        logger.error(f"❌ Error creando gráfico de distribución: {e}")
        return {"error": str(e), "type": "distribution_plot"}

def create_performance_chart(performance_data: Dict[str, float], 
                           title: str = "Performance Metrics") -> Dict[str, Any]:
    """
    Crea datos para un gráfico de métricas de rendimiento.
    
    Args:
        performance_data: Diccionario con métricas de rendimiento
        title: Título del gráfico
        
    Returns:
        Diccionario con datos para visualización
    """
    try:
        # Preparar datos para gráfico de barras
        metrics = list(performance_data.keys())
        values = list(performance_data.values())
        
        # Categorizar métricas por tipo
        return_metrics = [k for k in metrics if "cagr" in k.lower() or "return" in k.lower()]
        risk_metrics = [k for k in metrics if "drawdown" in k.lower() or "var" in k.lower()]
        ratio_metrics = [k for k in metrics if "sharpe" in k.lower() or "sortino" in k.lower()]
        other_metrics = [k for k in metrics if k not in return_metrics + risk_metrics + ratio_metrics]
        
        categories = {
            "return_metrics": return_metrics,
            "risk_metrics": risk_metrics,
            "ratio_metrics": ratio_metrics,
            "other_metrics": other_metrics
        }
        
        visualization_data = {
            "type": "performance_chart",
            "title": title,
            "metrics": metrics,
            "values": values,
            "categories": categories,
            "performance_data": performance_data
        }
        
        logger.info("✅ Datos de gráfico de rendimiento creados")
        return visualization_data
        
    except Exception as e:
        logger.error(f"❌ Error creando gráfico de rendimiento: {e}")
        return {"error": str(e), "type": "performance_chart"}

def create_comparison_plot(data1: pd.Series, data2: pd.Series, 
                          labels: Tuple[str, str] = ("Data 1", "Data 2"),
                          title: str = "Comparison Plot") -> Dict[str, Any]:
    """
    Crea datos para un gráfico de comparación entre dos series.
    
    Args:
        data1: Primera serie de datos
        data2: Segunda serie de datos
        labels: Etiquetas para las series
        title: Título del gráfico
        
    Returns:
        Diccionario con datos para visualización
    """
    try:
        # Calcular estadísticas comparativas
        comparison_stats = {
            "data1": {
                "mean": float(data1.mean()),
                "std": float(data1.std()),
                "count": len(data1)
            },
            "data2": {
                "mean": float(data2.mean()),
                "std": float(data2.std()),
                "count": len(data2)
            },
            "correlation": float(data1.corr(data2)) if len(data1) == len(data2) else None,
            "difference": float(data1.mean() - data2.mean())
        }
        
        visualization_data = {
            "type": "comparison_plot",
            "title": title,
            "data1": {
                "values": data1.tolist(),
                "label": labels[0]
            },
            "data2": {
                "values": data2.tolist(),
                "label": labels[1]
            },
            "comparison_stats": comparison_stats
        }
        
        logger.info("✅ Datos de gráfico de comparación creados")
        return visualization_data
        
    except Exception as e:
        logger.error(f"❌ Error creando gráfico de comparación: {e}")
        return {"error": str(e), "type": "comparison_plot"} 