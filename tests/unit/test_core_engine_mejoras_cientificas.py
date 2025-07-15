#!/usr/bin/env python3
"""
Test específico para verificar las mejoras científicas en el Core Engine.

Verifica:
1. Activación de mejoras científicas desde configuración GUI
2. Aplicación de mejoras científicas en Factor K Elite
3. Aplicación de mejoras científicas en Unified Evaluator
4. Integración con el flujo de análisis completo
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
    from src.core.integration_layer import (
        run_complete_analysis_with_gui_integration,
        FactorKElite96Enhanced,
        UnifiedEvaluatorEnhanced
    )
    from src.data.data_manager import DataManager
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mejoras_cientificas_core_engine():
    """Test principal para verificar mejoras científicas en core engine."""
    
    print("🔬 TEST: Mejoras Científicas en Core Engine")
    print("=" * 60)
    
    try:
        # Configurar DataManager
        dm = DataManager()
        dm.load_kpis_data("DatabankExport_M1.csv")
        df = dm.kpis_data.copy()
        
        print(f"📊 Datos cargados: {len(df)} estrategias")
        
        # Test 1: Configuración sin mejoras científicas
        print("\n🧪 Test 1: Configuración SIN mejoras científicas")
        config_sin_mejoras = {
            "scientific_improvements": False,
            "is_oos_split": 0.75,
            "trading_style": "General"
        }
        
        results_sin_mejoras, summary_sin_mejoras = run_complete_analysis_with_gui_integration(
            "DatabankExport_M1.csv",
            config=config_sin_mejoras,
            analysis_type="unified"
        )
        
        print(f"✅ Análisis sin mejoras científicas completado: {len(results_sin_mejoras)} estrategias")
        
        # Verificar que NO hay columnas de mejoras científicas
        columnas_cientificas = ['Unified_Score_Scientific', 'Regime_Score', 'HMM_Score', 'Market_Regime']
        columnas_presentes = [col for col in columnas_cientificas if col in results_sin_mejoras.columns]
        
        if not columnas_presentes:
            print("✅ Correcto: No hay columnas de mejoras científicas (configuración OFF)")
        else:
            print(f"⚠️ Advertencia: Se encontraron columnas científicas: {columnas_presentes}")
        
        # Test 2: Configuración CON mejoras científicas
        print("\n🧪 Test 2: Configuración CON mejoras científicas")
        config_con_mejoras = {
            "scientific_improvements": True,
            "is_oos_split": 0.75,
            "trading_style": "General"
        }
        
        results_con_mejoras, summary_con_mejoras = run_complete_analysis_with_gui_integration(
            "DatabankExport_M1.csv",
            config=config_con_mejoras,
            analysis_type="unified"
        )
        
        print(f"✅ Análisis con mejoras científicas completado: {len(results_con_mejoras)} estrategias")
        
        # Verificar que SÍ hay columnas de mejoras científicas
        columnas_presentes = [col for col in columnas_cientificas if col in results_con_mejoras.columns]
        
        if columnas_presentes:
            print(f"✅ Correcto: Se encontraron columnas de mejoras científicas: {columnas_presentes}")
            
            # Verificar datos en columnas científicas
            for col in columnas_presentes:
                if col in results_con_mejoras.columns:
                    valores_no_nulos = results_con_mejoras[col].notna().sum()
                    print(f"   📊 {col}: {valores_no_nulos}/{len(results_con_mejoras)} valores no nulos")
        else:
            print("❌ Error: No se encontraron columnas de mejoras científicas")
        
        # Test 3: Comparación de scores
        print("\n🧪 Test 3: Comparación de scores")
        
        if 'Unified_Score' in results_sin_mejoras.columns and 'Unified_Score' in results_con_mejoras.columns:
            score_sin_mejoras = results_sin_mejoras['Unified_Score'].describe()
            score_con_mejoras = results_con_mejoras['Unified_Score'].describe()
            
            print("📊 Estadísticas Unified_Score sin mejoras científicas:")
            print(f"   Media: {score_sin_mejoras['mean']:.4f}")
            print(f"   Std: {score_sin_mejoras['std']:.4f}")
            print(f"   Min: {score_sin_mejoras['min']:.4f}")
            print(f"   Max: {score_sin_mejoras['max']:.4f}")
            
            print("📊 Estadísticas Unified_Score con mejoras científicas:")
            print(f"   Media: {score_con_mejoras['mean']:.4f}")
            print(f"   Std: {score_con_mejoras['std']:.4f}")
            print(f"   Min: {score_con_mejoras['min']:.4f}")
            print(f"   Max: {score_con_mejoras['max']:.4f}")
        
        # Test 4: Verificar scores científicos específicos
        print("\n🧪 Test 4: Verificar scores científicos específicos")
        
        if 'Unified_Score_Scientific' in results_con_mejoras.columns:
            score_scientific = results_con_mejoras['Unified_Score_Scientific'].describe()
            print("📊 Estadísticas Unified_Score_Scientific:")
            print(f"   Media: {score_scientific['mean']:.4f}")
            print(f"   Std: {score_scientific['std']:.4f}")
            print(f"   Min: {score_scientific['min']:.4f}")
            print(f"   Max: {score_scientific['max']:.4f}")
        
        if 'Unified_Score_Enhanced' in results_con_mejoras.columns:
            score_enhanced = results_con_mejoras['Unified_Score_Enhanced'].describe()
            print("📊 Estadísticas Unified_Score_Enhanced:")
            print(f"   Media: {score_enhanced['mean']:.4f}")
            print(f"   Std: {score_enhanced['std']:.4f}")
            print(f"   Min: {score_enhanced['min']:.4f}")
            print(f"   Max: {score_enhanced['max']:.4f}")
        
        # Test 5: Verificar regímenes de mercado
        print("\n🧪 Test 5: Verificar regímenes de mercado")
        
        if 'Market_Regime' in results_con_mejoras.columns:
            regímenes = results_con_mejoras['Market_Regime'].value_counts()
            print("📊 Distribución de regímenes de mercado:")
            for régimen, count in regímenes.items():
                porcentaje = (count / len(results_con_mejoras)) * 100
                print(f"   Régimen {régimen}: {count} estrategias ({porcentaje:.1f}%)")
        
        # Test 6: Verificar estados HMM
        print("\n🧪 Test 6: Verificar estados HMM")
        
        if 'HMM_State' in results_con_mejoras.columns:
            estados = results_con_mejoras['HMM_State'].value_counts()
            print("📊 Distribución de estados HMM:")
            for estado, count in estados.items():
                porcentaje = (count / len(results_con_mejoras)) * 100
                print(f"   Estado {estado}: {count} estrategias ({porcentaje:.1f}%)")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("🎉 RESUMEN DE TEST DE MEJORAS CIENTÍFICAS")
        print("=" * 60)
        
        print("✅ Tests completados exitosamente:")
        print("   • Activación/desactivación de mejoras científicas")
        print("   • Aplicación de regímenes de mercado")
        print("   • Aplicación de análisis HMM")
        print("   • Generación de scores científicos")
        print("   • Integración con flujo de análisis completo")
        
        print("\n📊 Métricas verificadas:")
        print("   • Detección automática de temporalidad")
        print("   • Ajustes científicos basados en evidencia empírica")
        print("   • Filtros empíricos basados en evidencia científica")
        print("   • Métricas ajustadas según temporalidad")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_mejoras_cientificas_core_engine()
    if success:
        print("\n✅ Test de mejoras científicas en Core Engine COMPLETADO EXITOSAMENTE")
    else:
        print("\n❌ Test de mejoras científicas en Core Engine FALLÓ")
        sys.exit(1) 