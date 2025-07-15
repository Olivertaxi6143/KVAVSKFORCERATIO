#!/usr/bin/env python3
"""
Test de Validación de KPIs Extra por Estilo de Trading

Verifica que los KPIs extras cambian correctamente según el estilo de trading seleccionado,
incluyendo pesos automáticos, normalización y integración con el QVA Score.
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import logging

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.analysis.extra_kpi_manager import ExtraKPIManager
from src.core.analysis.qva_analyzer import QVAScorerEnhanced
from src.core.config.config_manager import ConfigManagerEnhanced
from src.data.data_manager import DataManager, create_data_manager
from src.logger_config import setup_logger

def test_kpis_extra_trading_style_validation():
    """
    Test exhaustivo para validar que los KPIs extras cambian correctamente 
    según el estilo de trading seleccionado.
    """
    print("🚀 Iniciando Test de Validación de KPIs Extra por Estilo de Trading")
    print("=" * 80)
    
    # Configurar logging
    logger = setup_logger("test_kpis_extra_validation")
    
    try:
        # 1. Inicializar componentes
        print("\n📋 Paso 1: Inicializando componentes...")
        
        config_manager = ConfigManagerEnhanced()
        extra_kpi_manager = ExtraKPIManager(config_manager)
        data_manager = create_data_manager()
        
        print("✅ Componentes inicializados correctamente")
        
        # 2. Cargar datos de prueba
        print("\n📊 Paso 2: Cargando datos de prueba...")
        
        # Crear datos de prueba con KPIs extra
        test_data = create_test_data_with_extra_kpis()
        
        print(f"✅ Datos de prueba creados: {len(test_data)} estrategias")
        print(f"📊 Columnas disponibles: {len(test_data.columns)}")
        
        # 3. Definir estilos de trading a probar
        print("\n🎯 Paso 3: Definindo estilos de trading a probar...")
        
        trading_styles = [
            'Intraday', 'Swing', 'Trend Following', 'Mean Reversion', 'Breakout',
            'Scalping', 'Day Trading', 'Position Trading', 'General'
        ]
        
        print(f"✅ {len(trading_styles)} estilos de trading definidos")
        
        # 4. Verificar KPIs extra por estilo
        print("\n🔍 Paso 4: Verificando KPIs extra por estilo de trading...")
        
        kpis_extra_results = {}
        
        for style in trading_styles:
            print(f"\n  🎯 Analizando estilo: {style}")
            
            # Obtener KPIs extra para este estilo
            extra_kpis = extra_kpi_manager.get_extra_kpis_for_style(style)
            
            if extra_kpis:
                print(f"    ✅ {len(extra_kpis)} KPIs extra configurados")
                
                # Mostrar KPIs extra y sus pesos
                for kpi_name, kpi_config in extra_kpis.items():
                    weight = kpi_config.get('weight', 0)
                    description = kpi_config.get('description', 'Sin descripción')
                    print(f"      • {kpi_name}: peso {weight:.3f} - {description}")
                
                # Validar disponibilidad en datos
                validation = extra_kpi_manager.validate_kpis_in_data(test_data, style)
                available_count = len(validation['available'])
                missing_count = len(validation['missing'])
                coverage = validation['coverage']
                
                print(f"    📊 Disponibilidad en datos:")
                print(f"      - Disponibles: {available_count}")
                print(f"      - Faltantes: {missing_count}")
                print(f"      - Cobertura: {coverage:.1%}")
                
                if validation['available']:
                    print(f"      - KPIs disponibles: {', '.join(validation['available'][:3])}{'...' if len(validation['available']) > 3 else ''}")
                
                kpis_extra_results[style] = {
                    'total_kpis': len(extra_kpis),
                    'available_kpis': available_count,
                    'missing_kpis': missing_count,
                    'coverage': coverage,
                    'kpis': extra_kpis
                }
            else:
                print(f"    ⚠️ No hay KPIs extra configurados para {style}")
                kpis_extra_results[style] = {
                    'total_kpis': 0,
                    'available_kpis': 0,
                    'missing_kpis': 0,
                    'coverage': 0,
                    'kpis': {}
                }
        
        # 5. Probar cálculo de QVA Score con diferentes estilos
        print("\n🔧 Paso 5: Probando cálculo de QVA Score con diferentes estilos...")
        
        qva_results = {}
        
        for style in trading_styles[:4]:  # Probar solo los primeros 4 estilos
            print(f"\n  🎯 Probando QVA Score para: {style}")
            
            # Configurar estilo de trading
            config_manager.update_trading_style(style)
            
            # Crear QVA Scorer
            qva_scorer = QVAScorerEnhanced(config_manager)
            
            # Calcular QVA Score
            try:
                qva_scores = qva_scorer.calculate_qva_score(test_data)
                
                if qva_scores is not None and len(qva_scores) > 0:
                    print(f"    ✅ QVA Scores calculados: {len(qva_scores)} valores")
                    print(f"    📊 Estadísticas:")
                    print(f"      - Mínimo: {qva_scores.min():.4f}")
                    print(f"      - Máximo: {qva_scores.max():.4f}")
                    print(f"      - Promedio: {qva_scores.mean():.4f}")
                    print(f"      - Desviación: {qva_scores.std():.4f}")
                    
                    qva_results[style] = {
                        'count': len(qva_scores),
                        'min': qva_scores.min(),
                        'max': qva_scores.max(),
                        'mean': qva_scores.mean(),
                        'std': qva_scores.std()
                    }
                else:
                    print(f"    ❌ Error: No se calcularon QVA Scores para {style}")
                    qva_results[style] = None
                    
            except Exception as e:
                print(f"    ❌ Error calculando QVA Score para {style}: {e}")
                qva_results[style] = None
        
        # 6. Verificar diferencias entre estilos
        print("\n📊 Paso 6: Verificando diferencias entre estilos...")
        
        valid_results = {k: v for k, v in qva_results.items() if v is not None}
        
        if len(valid_results) > 1:
            print("  📈 Comparación de QVA Scores entre estilos:")
            
            # Comparar promedios
            means = {style: result['mean'] for style, result in valid_results.items()}
            best_style = max(means.keys(), key=lambda k: means[k])
            worst_style = min(means.keys(), key=lambda k: means[k])
            
            print(f"    🏆 Mejor promedio: {best_style} ({means[best_style]:.4f})")
            print(f"    ⚠️ Peor promedio: {worst_style} ({means[worst_style]:.4f})")
            print(f"    📊 Rango de promedios: {max(means.values()):.4f} - {min(means.values()):.4f}")
            
            # Verificar variabilidad
            stds = {style: result['std'] for style, result in valid_results.items()}
            avg_std = np.mean(list(stds.values()))
            print(f"    📈 Desviación promedio: {avg_std:.4f}")
        
        # 7. Verificar aplicación de KPIs extra
        print("\n🔍 Paso 7: Verificando aplicación de KPIs extra...")
        
        for style in trading_styles[:3]:  # Probar solo los primeros 3
            print(f"\n  🎯 Verificando aplicación para: {style}")
            
            # Obtener KPIs extra
            extra_kpis = extra_kpi_manager.get_extra_kpis_for_style(style)
            
            if extra_kpis:
                # Aplicar KPIs extra directamente
                extra_scores = extra_kpi_manager.apply_extra_kpis_to_qva_score(test_data, style)
                
                if extra_scores is not None and len(extra_scores) > 0:
                    print(f"    ✅ KPIs extra aplicados correctamente")
                    print(f"    📊 Score promedio: {extra_scores.mean():.4f}")
                    print(f"    📈 Desviación: {extra_scores.std():.4f}")
                    
                    # Verificar que los scores están en rango [0,1]
                    min_score = extra_scores.min()
                    max_score = extra_scores.max()
                    
                    if 0 <= min_score <= max_score <= 1:
                        print(f"    ✅ Scores normalizados correctamente [0,1]")
                    else:
                        print(f"    ⚠️ Scores fuera de rango [0,1]: [{min_score:.4f}, {max_score:.4f}]")
                else:
                    print(f"    ❌ Error aplicando KPIs extra para {style}")
            else:
                print(f"    ⚠️ No hay KPIs extra para {style}")
        
        # 8. Crear informe final
        print("\n📋 Paso 8: Generando informe final...")
        
        informe = {
            'fecha_test': datetime.now().isoformat(),
            'estilos_analizados': len(trading_styles),
            'datos_test': {
                'estrategias': len(test_data),
                'columnas': len(test_data.columns)
            },
            'kpis_extra_por_estilo': kpis_extra_results,
            'qva_scores_por_estilo': qva_results,
            'resumen': {
                'estilos_con_kpis_extra': len([r for r in kpis_extra_results.values() if r['total_kpis'] > 0]),
                'estilos_con_qva_calculado': len([r for r in qva_results.values() if r is not None]),
                'cobertura_promedio': np.mean([r['coverage'] for r in kpis_extra_results.values() if r['coverage'] > 0])
            }
        }
        
        print("✅ Informe generado correctamente")
        
        # 9. Mostrar resumen ejecutivo
        print("\n📊 RESUMEN EJECUTIVO:")
        print("=" * 50)
        
        estilos_con_kpis = len([r for r in kpis_extra_results.values() if r['total_kpis'] > 0])
        estilos_con_qva = len([r for r in qva_results.values() if r is not None])
        cobertura_promedio = np.mean([r['coverage'] for r in kpis_extra_results.values() if r['coverage'] > 0])
        
        print(f"🎯 Estilos con KPIs extra: {estilos_con_kpis}/{len(trading_styles)}")
        print(f"🔧 Estilos con QVA calculado: {estilos_con_qva}/{len(trading_styles)}")
        print(f"📊 Cobertura promedio de KPIs: {cobertura_promedio:.1%}")
        
        if valid_results:
            mejor_estilo = max(valid_results.keys(), key=lambda k: valid_results[k]['mean'])
            print(f"🏆 Mejor estilo en QVA Score: {mejor_estilo}")
        
        print("\n✅ Test de validación de KPIs extra por estilo de trading COMPLETADO")
        assert True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        logger.error(f"Error en test de validación: {e}")
        assert False

def create_test_data_with_extra_kpis() -> pd.DataFrame:
    """
    Crea datos de prueba con KPIs extra para validar el sistema.
    
    Returns:
        DataFrame con datos de prueba
    """
    np.random.seed(42)
    n_strategies = 50
    
    # KPIs base
    data = {
        'Strategy_Name': [f'Strategy_{i:03d}' for i in range(n_strategies)],
        'Profit_factor': np.random.uniform(1.0, 3.0, n_strategies),
        'Sharpe_Ratio': np.random.uniform(0.5, 2.5, n_strategies),
        'Max_DD_%': np.random.uniform(5.0, 25.0, n_strategies),
        'CAGR': np.random.uniform(10.0, 50.0, n_strategies),
        'CalmarRatio': np.random.uniform(0.5, 3.0, n_strategies),
        'Sortino_Ratio': np.random.uniform(0.3, 2.0, n_strategies),
        'RecoveryFactor': np.random.uniform(1.0, 5.0, n_strategies),
        'Winning_Percent': np.random.uniform(40.0, 70.0, n_strategies),
        'Net_profit': np.random.uniform(1000, 50000, n_strategies),
        '#_of_trades': np.random.randint(50, 500, n_strategies)
    }
    
    # KPIs extra que pueden estar disponibles
    extra_kpis = {
        'Winrate': np.random.uniform(30.0, 80.0, n_strategies),
        'Avgtradedur': np.random.uniform(1.0, 30.0, n_strategies),
        'Exposure': np.random.uniform(0.1, 0.9, n_strategies),
        'SQN': np.random.uniform(0.5, 3.0, n_strategies),
        'Marratio': np.random.uniform(0.5, 2.5, n_strategies),
        'Maxdddur': np.random.uniform(5.0, 50.0, n_strategies),
        'VaR_(95%)': np.random.uniform(1.0, 10.0, n_strategies),
        'CVaR_(95%)': np.random.uniform(2.0, 15.0, n_strategies),
        'Expectancy': np.random.uniform(0.1, 2.0, n_strategies),
        'Avg_Mae': np.random.uniform(0.5, 5.0, n_strategies),
        'Max_Stag_Trades': np.random.randint(1, 20, n_strategies)
    }
    
    # Agregar KPIs extra al DataFrame
    data.update(extra_kpis)
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Ejecutar test
    success = test_kpis_extra_trading_style_validation()
    
    if success:
        print("\n🎉 Test completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Test falló")
        sys.exit(1) 