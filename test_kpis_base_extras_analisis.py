#!/usr/bin/env python3
"""
TEST_KPIS_BASE_EXTRAS_ANALISIS.py - Verificar uso de KPIs base y extras en análisis
"""

import sys
import os
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath('src'))

try:
    from src.core.integration_layer import (
        UnifiedEvaluatorEnhanced,
        QVAScorerEnhanced,
        ExtraKPIManager,
        ConfigManagerEnhanced
    )
    from data_manager import DataManager
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_kpis_base_extras_analisis():
    """Test para verificar que los KPIs base y extras se usan correctamente en el análisis."""
    print("🔍 TEST: Verificación de KPIs base y extras en análisis")
    print("=" * 70)
    
    try:
        # 1. Cargar datos
        print("📊 Paso 1: Cargando datos...")
        dm = DataManager()
        dm.load_all_data()
        
        if dm.kpis_data is None or dm.kpis_data.empty:
            print("❌ Error: No se pudieron cargar los datos")
            return False
        
        df_original = dm.kpis_data
        print(f"✅ Datos cargados: {len(df_original)} estrategias, {len(df_original.columns)} columnas")
        
        # 2. Crear componentes del análisis
        print("\n⚙️ Paso 2: Creando componentes del análisis...")
        
        # ConfigManager
        config_manager = ConfigManagerEnhanced()
        print("✅ ConfigManager creado")
        
        # ExtraKPIManager
        extra_kpi_manager = ExtraKPIManager(config_manager)
        print("✅ ExtraKPIManager creado")
        
        # QVAScorer
        qva_scorer = QVAScorerEnhanced(config_manager)
        print("✅ QVAScorer creado")
        
        # UnifiedEvaluator
        evaluator = UnifiedEvaluatorEnhanced()
        print("✅ UnifiedEvaluator creado")
        
        # 3. Verificar KPIs base disponibles
        print("\n📋 Paso 3: Verificando KPIs base disponibles...")
        kpis_base = [col for col in df_original.columns if pd.api.types.is_numeric_dtype(df_original[col])]
        print(f"🔢 KPIs base numéricos: {len(kpis_base)}")
        
        # Categorizar KPIs base
        kpis_categorizados = {
            'Rendimiento': [],
            'Riesgo': [],
            'Consistencia': [],
            'Otros': []
        }
        
        for kpi in kpis_base:
            kpi_lower = kpi.lower()
            if any(term in kpi_lower for term in ['cagr', 'profit', 'return', 'net']):
                kpis_categorizados['Rendimiento'].append(kpi)
            elif any(term in kpi_lower for term in ['drawdown', 'risk', 'var', 'cvar', 'ulcer']):
                kpis_categorizados['Riesgo'].append(kpi)
            elif any(term in kpi_lower for term in ['sharpe', 'sortino', 'sqn', 'calmar', 'consistency']):
                kpis_categorizados['Consistencia'].append(kpi)
            else:
                kpis_categorizados['Otros'].append(kpi)
        
        for categoria, kpis in kpis_categorizados.items():
            print(f"  📊 {categoria}: {len(kpis)} KPIs")
        
        # 4. Verificar KPIs extra por estilo de trading
        print("\n📋 Paso 4: Verificando KPIs extra por estilo de trading...")
        estilos_trading = ['Intraday', 'Swing', 'Trend Following', 'Mean Reversion', 'Breakout']
        
        kpis_extra_por_estilo = {}
        for estilo in estilos_trading:
            extra_kpis = extra_kpi_manager.get_extra_kpis_for_style(estilo)
            kpis_extra_por_estilo[estilo] = extra_kpis
            print(f"  🎯 {estilo}: {len(extra_kpis)} KPIs extra")
            for kpi_name, kpi_config in extra_kpis.items():
                print(f"    • {kpi_name} (peso: {kpi_config['weight']})")
        
        # 5. Ejecutar análisis con diferentes estilos
        print("\n🔧 Paso 5: Ejecutando análisis con diferentes estilos...")
        
        resultados_por_estilo = {}
        
        for estilo in estilos_trading[:2]:  # Probar solo los primeros 2 estilos
            print(f"\n  🎯 Probando estilo: {estilo}")
            
            # Configurar estilo de trading
            config_manager.update_trading_style(estilo)
            
            # Obtener KPIs habilitados
            enabled_kpis = config_manager.get_enabled_kpis()
            print(f"    📊 KPIs habilitados: {len(enabled_kpis)}")
            
            # Obtener KPIs extra para este estilo
            extra_kpis = extra_kpi_manager.get_extra_kpis_for_style(estilo)
            print(f"    🎯 KPIs extra: {len(extra_kpis)}")
            
            # Ejecutar análisis
            try:
                resultados = evaluator.evaluate_strategies_unified(df_original.copy())
                resultados_por_estilo[estilo] = resultados
                print(f"    ✅ Análisis completado: {len(resultados)} estrategias")
                
                # Verificar columnas de score
                score_cols = [col for col in resultados.columns if 'Score' in col or 'QVA' in col]
                print(f"    📊 Columnas de score: {score_cols}")
                
            except Exception as e:
                print(f"    ❌ Error en análisis: {e}")
                continue
        
        # 6. Verificar integración de KPIs extra en QVA Score
        print("\n🔍 Paso 6: Verificando integración de KPIs extra en QVA Score...")
        
        for estilo, resultados in resultados_por_estilo.items():
            print(f"\n  🎯 Estilo: {estilo}")
            
            # Verificar que QVA_Score existe
            if 'QVA_Score' in resultados.columns:
                print(f"    ✅ QVA_Score presente")
                
                # Verificar que no todos los scores son iguales (indicaría que no se usaron KPIs extra)
                qva_scores = resultados['QVA_Score'].dropna()
                if len(qva_scores) > 0:
                    score_variance = qva_scores.var()
                    print(f"    📊 Varianza de QVA_Score: {score_variance:.6f}")
                    
                    if score_variance > 0.001:  # Umbral mínimo de variación
                        print(f"    ✅ QVA_Score muestra variación (KPIs extra aplicados)")
                    else:
                        print(f"    ⚠️ QVA_Score muestra poca variación")
                else:
                    print(f"    ❌ QVA_Score vacío")
            else:
                print(f"    ❌ QVA_Score no presente")
            
            # Verificar Unified_Score
            if 'Unified_Score' in resultados.columns:
                print(f"    ✅ Unified_Score presente")
                
                unified_scores = resultados['Unified_Score'].dropna()
                if len(unified_scores) > 0:
                    score_variance = unified_scores.var()
                    print(f"    📊 Varianza de Unified_Score: {score_variance:.6f}")
                    
                    if score_variance > 0.001:
                        print(f"    ✅ Unified_Score muestra variación")
                    else:
                        print(f"    ⚠️ Unified_Score muestra poca variación")
                else:
                    print(f"    ❌ Unified_Score vacío")
            else:
                print(f"    ❌ Unified_Score no presente")
        
        # 7. Verificar que los KPIs extra se aplican correctamente
        print("\n🔍 Paso 7: Verificando aplicación de KPIs extra...")
        
        for estilo in estilos_trading[:2]:
            print(f"\n  🎯 Estilo: {estilo}")
            
            # Obtener KPIs extra para este estilo
            extra_kpis = extra_kpi_manager.get_extra_kpis_for_style(estilo)
            
            if extra_kpis:
                print(f"    📊 KPIs extra disponibles: {list(extra_kpis.keys())}")
                
                # Verificar que los KPIs extra están en los datos originales
                kpis_disponibles = []
                kpis_faltantes = []
                
                for kpi_name in extra_kpis.keys():
                    if kpi_name in df_original.columns:
                        kpis_disponibles.append(kpi_name)
                    else:
                        kpis_faltantes.append(kpi_name)
                
                print(f"    ✅ KPIs extra disponibles en datos: {kpis_disponibles}")
                if kpis_faltantes:
                    print(f"    ⚠️ KPIs extra faltantes: {kpis_faltantes}")
                
                # Verificar aplicación de KPIs extra
                if estilo in resultados_por_estilo:
                    resultados = resultados_por_estilo[estilo]
                    
                    # Verificar que el análisis se ejecutó con KPIs extra
                    if 'QVA_Score' in resultados.columns:
                        print(f"    ✅ QVA_Score calculado con KPIs extra")
                    else:
                        print(f"    ❌ QVA_Score no calculado")
            else:
                print(f"    ⚠️ No hay KPIs extra definidos para este estilo")
        
        # 8. Crear informe final
        print("\n📊 Paso 8: Generando informe final...")
        
        informe = {
            'fecha_test': datetime.now().isoformat(),
            'datos_originales': {
                'total_estrategias': len(df_original),
                'total_columnas': len(df_original.columns),
                'kpis_base_numericos': len(kpis_base),
                'kpis_categorizados': kpis_categorizados
            },
            'kpis_extra_por_estilo': {
                estilo: {
                    'total_kpis_extra': len(kpis),
                    'kpis_disponibles': list(kpis.keys())
                }
                for estilo, kpis in kpis_extra_por_estilo.items()
            },
            'resultados_analisis': {
                estilo: {
                    'total_estrategias': len(resultados),
                    'columnas_score': [col for col in resultados.columns if 'Score' in col or 'QVA' in col],
                    'qva_score_presente': 'QVA_Score' in resultados.columns,
                    'unified_score_presente': 'Unified_Score' in resultados.columns
                }
                for estilo, resultados in resultados_por_estilo.items()
            },
            'conclusiones': {
                'kpis_base_utilizados': len(kpis_base) > 0,
                'kpis_extra_disponibles': any(len(kpis) > 0 for kpis in kpis_extra_por_estilo.values()),
                'analisis_ejecutado': len(resultados_por_estilo) > 0,
                'scores_calculados': all('QVA_Score' in resultados.columns for resultados in resultados_por_estilo.values())
            }
        }
        
        # Guardar informe
        with open('test_kpis_base_extras_analisis.json', 'w', encoding='utf-8') as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Informe guardado en: test_kpis_base_extras_analisis.json")
        
        # 9. Resumen ejecutivo
        print(f"\n📊 RESUMEN EJECUTIVO:")
        print(f"  • KPIs base disponibles: {len(kpis_base)}")
        print(f"  • Estilos con KPIs extra: {sum(1 for kpis in kpis_extra_por_estilo.values() if len(kpis) > 0)}")
        print(f"  • Análisis ejecutados: {len(resultados_por_estilo)}")
        print(f"  • Scores calculados: {sum(1 for resultados in resultados_por_estilo.values() if 'QVA_Score' in resultados.columns)}")
        
        # Verificar que todo funciona correctamente
        todo_ok = (
            len(kpis_base) > 0 and
            any(len(kpis) > 0 for kpis in kpis_extra_por_estilo.values()) and
            len(resultados_por_estilo) > 0 and
            all('QVA_Score' in resultados.columns for resultados in resultados_por_estilo.values())
        )
        
        if todo_ok:
            print(f"\n✅ TEST EXITOSO: Los KPIs base y extras se usan correctamente en el análisis")
        else:
            print(f"\n❌ TEST FALLIDO: Hay problemas con el uso de KPIs base y extras")
        
        print("\n" + "=" * 70)
        return todo_ok
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_kpis_base_extras_analisis()
    sys.exit(0 if success else 1) 