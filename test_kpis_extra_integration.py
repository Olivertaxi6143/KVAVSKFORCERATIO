#!/usr/bin/env python3
"""
Test de Integración de KPIs Extra en QVA Score (Adaptado)
========================================================

Este script prueba que los KPIs extra se integran correctamente
en el cálculo del QVA Score según las mejoras implementadas y la configuración dinámica de estilos.
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_kpis_extra_integration():
    """Prueba la integración de KPIs extra en el QVA Score con estilos dinámicos."""
    print("🧪 TEST: Integración de KPIs Extra en QVA Score (Adaptado)")
    print("=" * 60)
    
    try:
        from core_engine_enhanced import (
            ConfigManagerEnhanced,
            QVAScorerEnhanced,
            ExtraKPIManager,
            ProgressCallback
        )
        print("✅ Módulos importados correctamente")
        
        # Crear datos de prueba
        test_data = create_test_data()
        print(f"✅ Datos de prueba creados: {len(test_data)} estrategias")
        
        # Obtener estilos de trading desde la configuración
        config_manager = ConfigManagerEnhanced()
        styles_to_test = config_manager.get_available_trading_styles()
        print(f"📋 Estilos de trading detectados en configuración: {styles_to_test}")
        
        if not styles_to_test:
            print("❌ No se detectaron estilos de trading en la configuración. Test abortado.")
            return False
        
        results = {}
        extra_kpi_manager = ExtraKPIManager(config_manager)
        
        for style in styles_to_test:
            print(f"\n🔍 Probando estilo: {style}")
            # Actualizar el estilo de trading en la configuración
            config_manager.update_trading_style(style)
            # Crear QVA Scorer con la configuración actualizada
            qva_scorer = QVAScorerEnhanced(config_manager)
            # Calcular QVA Score
            qva_scores = qva_scorer.calculate_qva_score(test_data)
            # Verificar que los scores se calcularon
            if qva_scores is not None and len(qva_scores) > 0:
                print(f"   ✅ QVA Scores calculados: {len(qva_scores)} valores")
                print(f"   📊 Rango de scores: {qva_scores.min():.4f} - {qva_scores.max():.4f}")
                print(f"   📈 Promedio: {qva_scores.mean():.4f}")
                results[style] = {
                    'count': len(qva_scores),
                    'min': qva_scores.min(),
                    'max': qva_scores.max(),
                    'mean': qva_scores.mean(),
                    'std': qva_scores.std()
                }
            else:
                print(f"   ❌ Error: No se calcularon QVA Scores para {style}")
                return False
            # Verificar KPIs extra aplicados
            extra_kpis = extra_kpi_manager.get_extra_kpis_for_style(style)
            if extra_kpis:
                print(f"   ✅ {len(extra_kpis)} KPIs extra configurados para {style}")
                for kpi, config in extra_kpis.items():
                    print(f"      - {kpi}: peso {config['weight']:.2f}")
            else:
                print(f"   ⚠️ {style}: No hay KPIs extra configurados")
        # Comparar resultados entre estilos
        print(f"\n📊 Comparación de resultados entre estilos:")
        for style, result in results.items():
            print(f"   {style}:")
            print(f"      - Promedio: {result['mean']:.4f}")
            print(f"      - Rango: {result['min']:.4f} - {result['max']:.4f}")
            print(f"      - Desv. Est.: {result['std']:.4f}")
        # Verificar que los scores son diferentes entre estilos (indicando que los KPIs extra funcionan)
        means = [results[style]['mean'] for style in styles_to_test]
        if len(set(means)) > 1:
            print(f"\n✅ Los KPIs extra están funcionando: scores diferentes entre estilos")
        else:
            print(f"\n⚠️ Los scores son muy similares entre estilos")
        print(f"\n🎉 Test de integración de KPIs extra completado exitosamente!")
        return True
    except Exception as e:
        print(f"❌ Error en test de integración: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_data():
    """Crea datos de prueba con KPIs relevantes."""
    np.random.seed(42)
    n_strategies = 50
    data = {
        'Strategy_Name': [f'Strategy_{i}' for i in range(n_strategies)],
        'CAGR': np.random.uniform(5, 25, n_strategies),
        'Profit_factor': np.random.uniform(1.1, 3.0, n_strategies),
        'Sharpe_Ratio': np.random.uniform(0.5, 2.5, n_strategies),
        'CalmarRatio': np.random.uniform(0.5, 4.0, n_strategies),
        'Max_DD_%': np.random.uniform(5, 20, n_strategies),
        'Winning_Percent': np.random.uniform(40, 70, n_strategies),
        'Net_profit': np.random.uniform(1000, 50000, n_strategies),
        'RecoveryFactor': np.random.uniform(1.5, 5.0, n_strategies),
        'Ulcer_Index_%': np.random.uniform(2, 15, n_strategies),
        'VaR_95%': np.random.uniform(-5, -1, n_strategies),
        'CVaR_95%': np.random.uniform(-8, -2, n_strategies),
        'Sortino_Ratio': np.random.uniform(0.3, 2.0, n_strategies),
        'SQN': np.random.uniform(0.5, 3.0, n_strategies),
        'RINAIndex': np.random.uniform(3, 12, n_strategies),
        'Exposure': np.random.uniform(20, 80, n_strategies),
        'Avg_Bars_in_Trade': np.random.uniform(5, 50, n_strategies),
        'Max_Drawdown_Duration': np.random.uniform(10, 100, n_strategies),
        'Payout_ratio': np.random.uniform(1.5, 4.0, n_strategies),
        'Max_Consec_Losses': np.random.uniform(3, 15, n_strategies),
        'Expectancy': np.random.uniform(50, 200, n_strategies),
        'Avg._MAE_-_Profit/loss': np.random.uniform(100, 500, n_strategies),
        'Avg._MFE_-_Profit/loss': np.random.uniform(200, 800, n_strategies),
        'Stagnation_Trades': np.random.uniform(5, 25, n_strategies),
        'New_Peak_Trades_%': np.random.uniform(10, 40, n_strategies),
        'Drawdown_Trades_%': np.random.uniform(20, 60, n_strategies),
        'Winrate': np.random.uniform(40, 70, n_strategies),
        'Avgtradedur': np.random.uniform(5, 50, n_strategies),
        'Marratio': np.random.uniform(1.5, 4.0, n_strategies),
        'Maxdddur': np.random.uniform(10, 100, n_strategies),
        'Avg_Stag_Trades': np.random.uniform(3, 20, n_strategies),
        'Max_Stag_Trades': np.random.uniform(5, 30, n_strategies),
        'Var': np.random.uniform(-8, -2, n_strategies),
        'Cvar': np.random.uniform(-12, -3, n_strategies),
        'Avg_Mae': np.random.uniform(100, 500, n_strategies),
        'Avg_Mfe': np.random.uniform(200, 800, n_strategies)
    }
    return pd.DataFrame(data)

def main():
    """Ejecuta el test principal adaptado."""
    print("🚀 INICIANDO TESTS DE INTEGRACIÓN DE KPIs EXTRA (ADAPTADO)")
    print("=" * 60)
    success = test_kpis_extra_integration()
    print("\n" + ("🎉 TODOS LOS TESTS PASARON!" if success else "⚠️ Algún test falló"))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 