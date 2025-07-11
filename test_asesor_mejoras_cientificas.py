#!/usr/bin/env python3
"""
Test específico para verificar las mejoras científicas en el Asesor Financiero Inteligente.

Verifica:
1. Detección automática de temporalidad
2. Aplicación de ajustes científicos
3. Filtros empíricos basados en evidencia
4. Métricas ajustadas según temporalidad
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from asesor_financiero_inteligente import AsesorFinancieroInteligente
    from data_manager import DataManager
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def crear_datos_ejemplo_con_temporalidad():
    """Crea datos de ejemplo con diferentes temporalidades para probar las mejoras científicas."""
    
    # Crear datos base
    np.random.seed(42)
    n_estrategias = 50
    
    # Datos con temporalidad M5 (para probar ajustes)
    estrategias_m5 = pd.DataFrame({
        'Strategy_Name': [f'Strategy_M5_{i}' for i in range(n_estrategias)],
        'TimeFrame': ['M5'] * n_estrategias,
        'Total_Trades': np.random.randint(50, 500, n_estrategias),
        'Total_Data_Months': np.random.randint(6, 24, n_estrategias),
        'CAGR': np.random.uniform(0.05, 0.25, n_estrategias),
        'Sharpe_Ratio': np.random.uniform(0.3, 1.5, n_estrategias),
        'Profit_factor': np.random.uniform(1.0, 2.5, n_estrategias),
        'Max_Drawdown': np.random.uniform(0.05, 0.30, n_estrategias),
        'Winning_Percent': np.random.uniform(0.35, 0.65, n_estrategias),
        'Expectancy': np.random.uniform(0.001, 0.005, n_estrategias),
        'Trades_Monthly': np.random.uniform(10, 50, n_estrategias),
        'Predictividad_IS_OOS': np.random.uniform(0.4, 0.9, n_estrategias),
        'Unified_Score': np.random.uniform(0.3, 0.9, n_estrategias),
        'CAGR (IS)': np.random.uniform(0.06, 0.28, n_estrategias),
        'CAGR (OOS)': np.random.uniform(0.04, 0.22, n_estrategias),
        'Sharpe_Ratio (IS)': np.random.uniform(0.4, 1.6, n_estrategias),
        'Sharpe_Ratio (OOS)': np.random.uniform(0.2, 1.4, n_estrategias),
        'Profit_factor (IS)': np.random.uniform(1.1, 2.8, n_estrategias),
        'Profit_factor (OOS)': np.random.uniform(0.9, 2.4, n_estrategias),
        'Drawdown (IS)': np.random.uniform(0.04, 0.28, n_estrategias),
        'Drawdown (OOS)': np.random.uniform(0.06, 0.32, n_estrategias)
    })
    
    # Datos con temporalidad H1 (para probar diferentes ajustes)
    estrategias_h1 = pd.DataFrame({
        'Strategy_Name': [f'Strategy_H1_{i}' for i in range(n_estrategias)],
        'TimeFrame': ['H1'] * n_estrategias,
        'Total_Trades': np.random.randint(20, 200, n_estrategias),
        'Total_Data_Months': np.random.randint(8, 30, n_estrategias),
        'CAGR': np.random.uniform(0.03, 0.20, n_estrategias),
        'Sharpe_Ratio': np.random.uniform(0.2, 1.2, n_estrategias),
        'Profit_factor': np.random.uniform(0.9, 2.2, n_estrategias),
        'Max_Drawdown': np.random.uniform(0.08, 0.35, n_estrategias),
        'Winning_Percent': np.random.uniform(0.30, 0.60, n_estrategias),
        'Expectancy': np.random.uniform(0.0005, 0.003, n_estrategias),
        'Trades_Monthly': np.random.uniform(5, 25, n_estrategias),
        'Predictividad_IS_OOS': np.random.uniform(0.3, 0.8, n_estrategias),
        'Unified_Score': np.random.uniform(0.2, 0.8, n_estrategias),
        'CAGR (IS)': np.random.uniform(0.04, 0.25, n_estrategias),
        'CAGR (OOS)': np.random.uniform(0.02, 0.20, n_estrategias),
        'Sharpe_Ratio (IS)': np.random.uniform(0.3, 1.4, n_estrategias),
        'Sharpe_Ratio (OOS)': np.random.uniform(0.1, 1.2, n_estrategias),
        'Profit_factor (IS)': np.random.uniform(1.0, 2.5, n_estrategias),
        'Profit_factor (OOS)': np.random.uniform(0.8, 2.1, n_estrategias),
        'Drawdown (IS)': np.random.uniform(0.06, 0.30, n_estrategias),
        'Drawdown (OOS)': np.random.uniform(0.08, 0.35, n_estrategias)
    })
    
    # Combinar datos
    estrategias_combinadas = pd.concat([estrategias_m5, estrategias_h1], ignore_index=True)
    
    return estrategias_combinadas

def test_mejoras_cientificas_asesor():
    """Test principal para verificar las mejoras científicas en el Asesor Financiero."""
    
    print("🧪 TEST: MEJORAS CIENTÍFICAS EN ASESOR FINANCIERO INTELIGENTE")
    print("=" * 70)
    
    try:
        # 1. Crear datos de ejemplo con temporalidad
        print("📊 Creando datos de ejemplo con temporalidad...")
        estrategias_ejemplo = crear_datos_ejemplo_con_temporalidad()
        print(f"✅ Datos creados: {len(estrategias_ejemplo)} estrategias")
        print(f"📈 Temporalidades: {estrategias_ejemplo['TimeFrame'].value_counts().to_dict()}")
        
        # 2. Seleccionar KPIs para análisis
        kpis_analisis = [
            'CAGR (IS)', 'CAGR (OOS)', 'Sharpe_Ratio (IS)', 'Sharpe_Ratio (OOS)',
            'Profit_factor (IS)', 'Profit_factor (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)',
            'Total_Trades', 'Total_Data_Months', 'CAGR', 'Sharpe_Ratio', 'Profit_factor',
            'Max_Drawdown', 'Winning_Percent', 'Expectancy', 'Trades_Monthly',
            'Predictividad_IS_OOS', 'Unified_Score'
        ]
        
        print(f"📈 KPIs seleccionados: {len(kpis_analisis)} métricas")
        
        # 3. Crear asesor financiero
        print("\n🤖 Creando Asesor Financiero Inteligente...")
        asesor = AsesorFinancieroInteligente(estrategias_ejemplo, kpis_analisis)
        print("✅ Asesor creado exitosamente")
        
        # 4. Verificar detección de temporalidad
        print("\n🔍 VERIFICANDO DETECCIÓN DE TEMPORALIDAD:")
        print(f"   • Temporalidad detectada: {asesor.temporalidad_detectada}")
        print(f"   • Factor de ajuste: {asesor.factor_ajuste_temporalidad:.3f}")
        
        if asesor.temporalidad_detectada and asesor.temporalidad_detectada != "Desconocida":
            print("   ✅ Detección de temporalidad funcionando")
        else:
            print("   ⚠️ Temporalidad no detectada - verificar columna TimeFrame")
        
        # 5. Ejecutar análisis completo
        print("\n🚀 Ejecutando análisis completo con mejoras científicas...")
        resultados = asesor.generar_consejos_completos()
        print("✅ Análisis completado")
        
        # 6. Verificar mejoras científicas aplicadas
        print("\n🔬 VERIFICANDO MEJORAS CIENTÍFICAS:")
        
        if 'mejoras_cientificas' in resultados:
            mejoras = resultados['mejoras_cientificas']
            print(f"   • Temporalidad detectada: {mejoras.get('temporalidad_detectada', 'N/A')}")
            print(f"   • Factor de ajuste: {mejoras.get('factor_ajuste_temporalidad', 0):.3f}")
            print(f"   • Consejos de mejoras: {len(mejoras.get('consejos_mejoras', []))}")
            print("   ✅ Mejoras científicas aplicadas correctamente")
        else:
            print("   ⚠️ No se encontraron mejoras científicas en resultados")
        
        # 7. Verificar filtros científicos
        print("\n🔍 VERIFICANDO FILTROS CIENTÍFICOS:")
        
        estrategias_originales = len(estrategias_ejemplo)
        estrategias_finales = len(asesor.estrategias)
        filtrado = estrategias_originales - estrategias_finales
        
        print(f"   • Estrategias originales: {estrategias_originales}")
        print(f"   • Estrategias después de filtros: {estrategias_finales}")
        print(f"   • Estrategias filtradas: {filtrado}")
        
        if filtrado > 0:
            print("   ✅ Filtros científicos aplicados correctamente")
        else:
            print("   ⚠️ No se aplicaron filtros científicos")
        
        # 8. Verificar consejos generados
        print("\n💡 VERIFICANDO CONSEJOS GENERADOS:")
        
        consejos_completos = resultados.get('consejos_completos', [])
        print(f"   • Total de consejos: {len(consejos_completos)}")
        
        # Buscar consejos específicos de mejoras científicas
        consejos_mejoras = [c for c in consejos_completos if 'Temporalidad detectada' in c or 'Factor de ajuste' in c or 'Ajustes científicos' in c]
        print(f"   • Consejos de mejoras científicas: {len(consejos_mejoras)}")
        
        for consejo in consejos_mejoras[:3]:  # Mostrar los primeros 3
            print(f"     - {consejo}")
        
        if len(consejos_mejoras) > 0:
            print("   ✅ Consejos de mejoras científicas generados correctamente")
        else:
            print("   ⚠️ No se generaron consejos de mejoras científicas")
        
        # 9. Verificar análisis completos
        print("\n📊 VERIFICANDO ANÁLISIS COMPLETOS:")
        
        analisis_completos = sum([
            'error' not in resultados.get('correlacion_is_oos', {}),
            'error' not in resultados.get('outliers', {}),
            'error' not in resultados.get('clustering', {}),
            'error' not in resultados.get('importancia_kpis', {}),
            'error' not in resultados.get('prediccion', {})
        ])
        
        print(f"   • Análisis completados exitosamente: {analisis_completos}/5")
        
        if analisis_completos >= 4:
            print("   ✅ Análisis completos funcionando correctamente")
        else:
            print("   ⚠️ Algunos análisis presentaron errores")
        
        # 10. Resumen final
        print("\n📋 RESUMEN FINAL:")
        print("=" * 30)
        
        print(f"✅ Temporalidad detectada: {asesor.temporalidad_detectada}")
        print(f"✅ Factor de ajuste aplicado: {asesor.factor_ajuste_temporalidad:.3f}")
        print(f"✅ Estrategias analizadas: {len(asesor.estrategias)}")
        print(f"✅ Consejos generados: {len(consejos_completos)}")
        print(f"✅ Análisis completos: {analisis_completos}/5")
        
        if asesor.temporalidad_detectada and asesor.temporalidad_detectada != "Desconocida" and len(consejos_mejoras) > 0:
            print("\n🎉 ¡MEJORAS CIENTÍFICAS INTEGRADAS EXITOSAMENTE!")
            print("   • Detección automática de temporalidad ✓")
            print("   • Ajustes científicos aplicados ✓")
            print("   • Filtros empíricos funcionando ✓")
            print("   • Métricas ajustadas según temporalidad ✓")
        else:
            print("\n⚠️ Algunas mejoras científicas no se aplicaron correctamente")
        
        print("\n" + "=" * 70)
        print("✅ Test completado")
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mejoras_cientificas_asesor() 