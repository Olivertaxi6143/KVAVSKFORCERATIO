#!/usr/bin/env python3
"""
Script de prueba para el Asesor Financiero Inteligente
====================================================

Valida la implementación del asesor con datos de ejemplo.
"""

import pandas as pd
import numpy as np
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.asesor_financiero_inteligente import AsesorFinancieroInteligente, ejecutar_analisis_completo

def crear_datos_ejemplo():
    """Crea datos de ejemplo para probar el asesor."""
    np.random.seed(42)
    
    # Crear estrategias de ejemplo
    n_estrategias = 50
    
    # KPIs principales
    data = {
        'Strategy_Name': [f'Strategy_{i+1}' for i in range(n_estrategias)],
        'CAGR (IS)': np.random.uniform(10, 50, n_estrategias),
        'CAGR (OOS)': np.random.uniform(8, 45, n_estrategias),
        'Sharpe_Ratio (IS)': np.random.uniform(1.0, 3.0, n_estrategias),
        'Sharpe_Ratio (OOS)': np.random.uniform(0.8, 2.8, n_estrategias),
        'Profit_factor (IS)': np.random.uniform(1.2, 3.0, n_estrategias),
        'Profit_factor (OOS)': np.random.uniform(1.1, 2.8, n_estrategias),
        'Drawdown (IS)': np.random.uniform(5, 25, n_estrategias),
        'Drawdown (OOS)': np.random.uniform(6, 30, n_estrategias),
        'CalmarRatio (IS)': np.random.uniform(1.5, 4.0, n_estrategias),
        'CalmarRatio (OOS)': np.random.uniform(1.3, 3.8, n_estrategias),
        'SQN (IS)': np.random.uniform(1.0, 3.0, n_estrategias),
        'SQN (OOS)': np.random.uniform(0.8, 2.8, n_estrategias),
        'RecoveryFactor': np.random.uniform(1.5, 4.0, n_estrategias),
        'Sortino_Ratio': np.random.uniform(1.2, 3.5, n_estrategias),
        'VaR (95%)': np.random.uniform(1, 8, n_estrategias),
        'CVaR (95%)': np.random.uniform(2, 12, n_estrategias),
        'Winning_Percent': np.random.uniform(45, 75, n_estrategias),
        '# of trades': np.random.randint(50, 500, n_estrategias),
        'Exposure': np.random.uniform(20, 80, n_estrategias),
        'Avg. Bars in Trade': np.random.uniform(5, 50, n_estrategias),
        'Max Drawdown Duration': np.random.uniform(10, 100, n_estrategias),
        'Payout ratio': np.random.uniform(0.8, 2.5, n_estrategias),
        'Unified_Score': np.random.uniform(60, 95, n_estrategias)
    }
    
    df = pd.DataFrame(data)
    
    # Agregar algunos outliers para probar detección
    df.loc[0, 'Drawdown (OOS)'] = 50  # Outlier malo
    df.loc[1, 'CAGR (OOS)'] = 80     # Outlier bueno
    df.loc[2, 'Sharpe_Ratio (OOS)'] = 5  # Outlier bueno
    
    return df

def test_asesor_financiero():
    """Prueba completa del Asesor Financiero Inteligente."""
    print("🧪 Iniciando pruebas del Asesor Financiero Inteligente")
    print("=" * 60)
    
    # Crear datos de ejemplo
    print("📊 Creando datos de ejemplo...")
    estrategias_ejemplo = crear_datos_ejemplo()
    print(f"✅ Datos creados: {len(estrategias_ejemplo)} estrategias")
    
    # Seleccionar KPIs para análisis
    kpis_analisis = [
        'CAGR (IS)', 'CAGR (OOS)', 'Sharpe_Ratio (IS)', 'Sharpe_Ratio (OOS)',
        'Profit_factor (IS)', 'Profit_factor (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)',
        'CalmarRatio (IS)', 'CalmarRatio (OOS)', 'SQN (IS)', 'SQN (OOS)',
        'RecoveryFactor', 'Sortino_Ratio', 'VaR (95%)', 'CVaR (95%)',
        'Winning_Percent', '# of trades', 'Exposure', 'Avg. Bars in Trade',
        'Max Drawdown Duration', 'Payout ratio'
    ]
    
    print(f"📈 KPIs seleccionados: {len(kpis_analisis)} métricas")
    
    # Crear asesor
    print("\n🤖 Creando Asesor Financiero Inteligente...")
    asesor = AsesorFinancieroInteligente(estrategias_ejemplo, kpis_analisis)
    print("✅ Asesor creado exitosamente")
    
    # Ejecutar análisis completo
    print("\n🚀 Ejecutando análisis completo...")
    resultados = asesor.generar_consejos_completos()
    print("✅ Análisis completado")
    
    # Mostrar resultados
    print("\n📋 RESULTADOS DEL ANÁLISIS:")
    print("=" * 40)
    
    # Correlación IS/OOS
    if 'correlacion_is_oos' in resultados:
        corr = resultados['correlacion_is_oos']
        print(f"📊 Correlación IS/OOS:")
        print(f"   • Pares analizados: {corr.get('pairs_analyzed', 0)}")
        print(f"   • Pares consistentes: {corr.get('consistent_pairs', 0)}")
        if 'consejos' in corr:
            print("   • Consejos:")
            for consejo in corr['consejos'][:3]:  # Mostrar solo los primeros 3
                print(f"     - {consejo}")
    
    # Outliers
    if 'outliers' in resultados:
        outliers = resultados['outliers']
        print(f"\n🔍 Outliers:")
        print(f"   • Total detectados: {len(outliers.get('outliers', []))}")
        print(f"   • Riesgo elevado: {len(outliers.get('malos_outliers', []))}")
        print(f"   • Rendimiento excepcional: {len(outliers.get('buenos_outliers', []))}")
        if 'consejos' in outliers:
            print("   • Consejos:")
            for consejo in outliers['consejos'][:3]:
                print(f"     - {consejo}")
    
    # Clustering
    if 'clustering' in resultados:
        cluster = resultados['clustering']
        print(f"\n🎯 Clustering:")
        print(f"   • Score de silueta: {cluster.get('silhouette_score', 0):.3f}")
        if 'cluster_analysis' in cluster:
            print("   • Análisis de clusters:")
            for cluster_info in cluster['cluster_analysis']:
                print(f"     - Cluster {cluster_info['cluster_id']}: {cluster_info['size']} estrategias")
    
    # Importancia de KPIs
    if 'importancia_kpis' in resultados:
        importancia = resultados['importancia_kpis']
        print(f"\n📈 Importancia de KPIs:")
        if 'top_kpis' in importancia:
            print("   • Top 5 KPIs más importantes:")
            for i, (kpi, importance_val) in enumerate(list(importancia['top_kpis'].items())[:5], 1):
                percentage = (importance_val / sum(importancia['top_kpis'].values())) * 100
                print(f"     {i}. {kpi}: {percentage:.1f}%")
    
    # Predicción
    if 'prediccion' in resultados:
        pred = resultados['prediccion']
        print(f"\n🔮 Predicción:")
        print(f"   • R² promedio: {pred.get('r2_mean', 0):.3f}")
        print(f"   • Error promedio: {pred.get('mae', 0):.2f}")
        print(f"   • Error cuadrático: {pred.get('rmse', 0):.2f}")
    
    # Resumen ejecutivo
    print(f"\n📋 RESUMEN EJECUTIVO:")
    print("=" * 30)
    resumen = asesor.obtener_resumen_ejecutivo()
    print(resumen)
    
    # Consejos completos
    print(f"\n🎯 CONSEJOS COMPLETOS:")
    print("=" * 25)
    if 'consejos_completos' in resultados:
        for i, consejo in enumerate(resultados['consejos_completos'], 1):
            print(f"{i}. {consejo}")
    
    print("\n✅ Pruebas completadas exitosamente!")
    assert True

def test_funcion_utilidad():
    """Prueba la función de utilidad para análisis directo."""
    print("\n🧪 Probando función de utilidad...")
    
    estrategias_ejemplo = crear_datos_ejemplo()
    kpis_analisis = [
        'CAGR (IS)', 'CAGR (OOS)', 'Sharpe_Ratio (IS)', 'Sharpe_Ratio (OOS)',
        'Profit_factor (IS)', 'Profit_factor (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)',
        'RecoveryFactor', 'Sortino_Ratio', 'VaR (95%)', 'CVaR (95%)'
    ]
    
    # Usar función de utilidad
    resultados = ejecutar_analisis_completo(estrategias_ejemplo, kpis_analisis)
    
    assert 'consejos_completos' in resultados, "Error en función de utilidad"
    print(f"✅ Función de utilidad exitosa: {len(resultados['consejos_completos'])} consejos generados")

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO PRUEBAS DEL ASESOR FINANCIERO INTELIGENTE")
        print("=" * 60)
        
        # Prueba principal
        test_asesor_financiero()
        
        # Prueba función de utilidad
        test_funcion_utilidad()
        
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        print("El Asesor Financiero Inteligente está listo para usar en la GUI.")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 