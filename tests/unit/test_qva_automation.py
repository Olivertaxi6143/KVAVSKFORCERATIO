#!/usr/bin/env python3
"""
Test de automatización de pesos y penalizaciones para QVAScorerEnhanced

Valida que la automatización funcione correctamente con:
- Diferentes estilos de trading
- Optimización automática de pesos
- Optimización automática de penalizaciones
- Reportes de optimización
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

# Importar módulos del proyecto
from src.core.integration_layer import QVAScorerEnhanced
from src.data.data_manager import create_data_manager
from src.core.config.config_manager import ConfigManagerEnhanced
from src.logger_config import setup_logger

# Configurar logging
logger = setup_logger("test_qva_automation")

def test_automation_by_trading_style():
    """Test de automatización para diferentes estilos de trading."""
    
    logger.info("🧪 Iniciando test de automatización por estilo de trading")
    
    try:
        # Crear datos de prueba con diferentes características
        test_data = create_test_data_for_styles()
        
        # Crear QVA Enhanced
        qva_enhanced = QVAScorerEnhanced()
        
        # Estilos de trading a probar
        trading_styles = ['Scalping', 'Day Trading', 'Swing Trading', 'Position Trading', 'General']
        
        results = {}
        
        for style in trading_styles:
            logger.info(f"🎯 Probando automatización para: {style}")
            
            # Obtener datos específicos para el estilo
            df = test_data.get(style, test_data['General'])
            
            # Optimizar pesos automáticamente
            optimized_weights = qva_enhanced.auto_optimize_weights_by_trading_style(style, df)
            
            # Optimizar penalizaciones automáticamente
            optimized_penalties = qva_enhanced.auto_optimize_penalties_by_trading_style(style, df)
            
            # Generar reporte de optimización
            optimization_report = qva_enhanced.get_optimization_report(style, df)
            
            # Validaciones
            assert len(optimized_weights) == 4, f"❌ Pesos incorrectos para {style}"
            assert sum(optimized_weights.values()) > 0.99, f"❌ Pesos no normalizados para {style}"
            assert len(optimized_penalties) >= 5, f"❌ Penalizaciones insuficientes para {style}"
            assert 'trading_style' in optimization_report, f"❌ Reporte incompleto para {style}"
            
            results[style] = {
                'weights': optimized_weights,
                'penalties': optimized_penalties,
                'report': optimization_report
            }
            
            logger.info(f"✅ {style}: Pesos={optimized_weights}, Penalizaciones={len(optimized_penalties)}")
        
        # Validar diferencias entre estilos
        validate_style_differences(results)
        
        logger.info("🎉 Test de automatización completado exitosamente")
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test de automatización: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        assert False

def create_test_data_for_styles():
    """Crea datos de prueba específicos para cada estilo de trading."""
    
    np.random.seed(42)  # Para reproducibilidad
    
    # Datos base
    n_strategies = 50
    
    test_data = {}
    
    # Scalping: Alta frecuencia, pequeñas ganancias, alta consistencia
    scalping_data = {
        'Strategy_Name': [f'Scalping_{i}' for i in range(n_strategies)],
        'CAGR': np.random.uniform(0.5, 2.0, n_strategies),  # Ganancias pequeñas
        'Sharpe_Ratio': np.random.uniform(1.5, 3.0, n_strategies),  # Alto Sharpe
        'Profit_factor': np.random.uniform(1.1, 1.5, n_strategies),  # PF moderado
        'Drawdown': np.random.uniform(2.0, 8.0, n_strategies),  # DD bajo
        'Winning_Percent': np.random.uniform(0.6, 0.8, n_strategies),  # Alto % victorias
        'Exposure': np.random.uniform(0.1, 0.4, n_strategies),  # Baja exposición
        'Max_Consec_Losses': np.random.randint(2, 6, n_strategies),  # Pocas pérdidas consecutivas
        'Stagnation': np.random.randint(3, 8, n_strategies),  # Poco estancamiento
        'Avg_Bars_in_Trade': np.random.uniform(5, 20, n_strategies),  # Trades cortos
        'CalmarRatio': np.random.uniform(2.0, 5.0, n_strategies),  # Alto Calmar
        'SQN': np.random.uniform(1.5, 3.0, n_strategies),  # Alto SQN
        'RINAIndex': np.random.uniform(0.8, 1.2, n_strategies)  # Alto RINA
    }
    test_data['Scalping'] = pd.DataFrame(scalping_data)
    
    # Day Trading: Frecuencia media, ganancias moderadas
    day_trading_data = {
        'Strategy_Name': [f'DayTrading_{i}' for i in range(n_strategies)],
        'CAGR': np.random.uniform(1.0, 4.0, n_strategies),  # Ganancias moderadas
        'Sharpe_Ratio': np.random.uniform(1.0, 2.5, n_strategies),  # Sharpe moderado
        'Profit_factor': np.random.uniform(1.2, 2.0, n_strategies),  # PF bueno
        'Drawdown': np.random.uniform(5.0, 15.0, n_strategies),  # DD moderado
        'Winning_Percent': np.random.uniform(0.4, 0.7, n_strategies),  # % victorias moderado
        'Exposure': np.random.uniform(0.2, 0.6, n_strategies),  # Exposición moderada
        'Max_Consec_Losses': np.random.randint(3, 8, n_strategies),  # Pérdidas consecutivas moderadas
        'Stagnation': np.random.randint(5, 15, n_strategies),  # Estancamiento moderado
        'CalmarRatio': np.random.uniform(1.0, 3.0, n_strategies),  # Calmar moderado
        'SQN': np.random.uniform(1.0, 2.5, n_strategies),  # SQN moderado
        'Max_DD_pct': np.random.uniform(3.0, 12.0, n_strategies),  # DD % moderado
        'VaR_95pct': np.random.uniform(-2.0, -0.5, n_strategies)  # VaR moderado
    }
    test_data['Day Trading'] = pd.DataFrame(day_trading_data)
    
    # Swing Trading: Frecuencia baja, ganancias mayores
    swing_trading_data = {
        'Strategy_Name': [f'SwingTrading_{i}' for i in range(n_strategies)],
        'CAGR': np.random.uniform(2.0, 6.0, n_strategies),  # Ganancias mayores
        'Sharpe_Ratio': np.random.uniform(0.8, 2.0, n_strategies),  # Sharpe variable
        'Profit_factor': np.random.uniform(1.3, 2.5, n_strategies),  # PF bueno
        'Drawdown': np.random.uniform(8.0, 20.0, n_strategies),  # DD mayor
        'Winning_Percent': np.random.uniform(0.3, 0.6, n_strategies),  # % victorias variable
        'Exposure': np.random.uniform(0.3, 0.7, n_strategies),  # Exposición mayor
        'Max_Consec_Losses': np.random.randint(4, 10, n_strategies),  # Más pérdidas consecutivas
        'Stagnation': np.random.randint(8, 20, n_strategies),  # Más estancamiento
        'RecoveryFactor': np.random.uniform(1.5, 4.0, n_strategies),  # RF bueno
        'CalmarRatio': np.random.uniform(0.8, 2.5, n_strategies),  # Calmar variable
        'RINAIndex': np.random.uniform(0.6, 1.0, n_strategies),  # RINA variable
        'CVaR_95pct': np.random.uniform(-3.0, -1.0, n_strategies)  # CVaR mayor
    }
    test_data['Swing Trading'] = pd.DataFrame(swing_trading_data)
    
    # Position Trading: Frecuencia muy baja, ganancias grandes
    position_trading_data = {
        'Strategy_Name': [f'PositionTrading_{i}' for i in range(n_strategies)],
        'CAGR': np.random.uniform(3.0, 8.0, n_strategies),  # Ganancias grandes
        'Sharpe_Ratio': np.random.uniform(0.6, 1.8, n_strategies),  # Sharpe variable
        'Profit_factor': np.random.uniform(1.5, 3.0, n_strategies),  # PF muy bueno
        'Drawdown': np.random.uniform(12.0, 25.0, n_strategies),  # DD grande
        'Winning_Percent': np.random.uniform(0.25, 0.55, n_strategies),  # % victorias bajo
        'Exposure': np.random.uniform(0.4, 0.8, n_strategies),  # Exposición alta
        'Max_Consec_Losses': np.random.randint(5, 12, n_strategies),  # Muchas pérdidas consecutivas
        'Stagnation': np.random.randint(12, 25, n_strategies),  # Mucho estancamiento
        'RecoveryFactor': np.random.uniform(2.0, 5.0, n_strategies),  # RF muy bueno
        'SQN': np.random.uniform(0.8, 2.0, n_strategies),  # SQN variable
        'Max_DD_pct': np.random.uniform(8.0, 20.0, n_strategies),  # DD % grande
        'Ulcer_Index_pct': np.random.uniform(5.0, 15.0, n_strategies)  # UI mayor
    }
    test_data['Position Trading'] = pd.DataFrame(position_trading_data)
    
    # General: Mezcla de características
    general_data = {
        'Strategy_Name': [f'General_{i}' for i in range(n_strategies)],
        'CAGR': np.random.uniform(1.5, 5.0, n_strategies),
        'Sharpe_Ratio': np.random.uniform(0.8, 2.2, n_strategies),
        'Profit_factor': np.random.uniform(1.2, 2.2, n_strategies),
        'Drawdown': np.random.uniform(5.0, 18.0, n_strategies),
        'Winning_Percent': np.random.uniform(0.35, 0.65, n_strategies),
        'Exposure': np.random.uniform(0.2, 0.7, n_strategies),
        'Max_Consec_Losses': np.random.randint(3, 9, n_strategies),
        'Stagnation': np.random.randint(5, 18, n_strategies),
        'CalmarRatio': np.random.uniform(0.8, 3.0, n_strategies),
        'SQN': np.random.uniform(0.8, 2.2, n_strategies),
        'Max_DD_pct': np.random.uniform(4.0, 15.0, n_strategies)
    }
    test_data['General'] = pd.DataFrame(general_data)
    
    return test_data

def validate_style_differences(results):
    """Valida que los estilos tengan configuraciones diferentes."""
    
    logger.info("🔍 Validando diferencias entre estilos")
    
    # Comparar pesos entre estilos
    styles = list(results.keys())
    
    for i, style1 in enumerate(styles):
        for j, style2 in enumerate(styles[i+1:], i+1):
            weights1 = results[style1]['weights']
            weights2 = results[style2]['weights']
            
            # Calcular diferencia promedio
            avg_diff = sum(abs(weights1[k] - weights2[k]) for k in weights1.keys()) / len(weights1)
            
            logger.info(f"📊 Diferencia {style1} vs {style2}: {avg_diff:.4f}")
            
            # Verificar que hay diferencias significativas
            assert avg_diff > 0.01, f"❌ Diferencias insuficientes entre {style1} y {style2}"
    
    # Validar características específicas por estilo
    validate_scalping_characteristics(results.get('Scalping', {}))
    validate_position_trading_characteristics(results.get('Position Trading', {}))
    
    logger.info("✅ Diferencias entre estilos validadas")

def validate_scalping_characteristics(scalping_result):
    """Valida características específicas del scalping."""
    
    if not scalping_result:
        return
    
    weights = scalping_result.get('weights', {})
    penalties = scalping_result.get('penalties', {})
    
    # Scalping debería tener mayor peso en consistencia
    assert weights.get('consistency', 0) >= 0.25, "❌ Scalping: consistencia muy baja"
    
    # Scalping debería tener menor peso en rentabilidad
    assert weights.get('profitability', 0) <= 0.4, "❌ Scalping: rentabilidad muy alta"
    
    # Penalizaciones de scalping deberían ser más estrictas
    consecutive_penalty = penalties.get('consecutive_losses', {})
    if consecutive_penalty.get('enabled', False):
        assert consecutive_penalty.get('threshold', 10) <= 8, "❌ Scalping: threshold de pérdidas consecutivas muy alto"
    
    logger.info("✅ Características de scalping validadas")

def validate_position_trading_characteristics(position_result):
    """Valida características específicas del position trading."""
    
    if not position_result:
        return
    
    weights = position_result.get('weights', {})
    penalties = position_result.get('penalties', {})
    
    # Position trading debería tener mayor peso en rentabilidad
    assert weights.get('profitability', 0) >= 0.45, "❌ Position Trading: rentabilidad muy baja"
    
    # Position trading debería tener menor peso en riesgo
    assert weights.get('risk', 0) <= 0.3, "❌ Position Trading: riesgo muy alto"
    
    # Penalizaciones de position trading deberían ser menos estrictas
    stagnation_penalty = penalties.get('stagnation', {})
    if stagnation_penalty.get('enabled', False):
        assert stagnation_penalty.get('threshold', 5) >= 12, "❌ Position Trading: threshold de estancamiento muy bajo"
    
    logger.info("✅ Características de position trading validadas")

def test_optimization_report():
    """Test específico del reporte de optimización."""
    
    logger.info("🧪 Iniciando test de reporte de optimización")
    
    try:
        # Crear datos de prueba
        test_data = create_test_data_for_styles()
        df = test_data['Day Trading']
        
        # Crear QVA Enhanced
        qva_enhanced = QVAScorerEnhanced()
        
        # Generar reporte
        report = qva_enhanced.get_optimization_report('Day Trading', df)
        
        # Validaciones del reporte
        assert 'trading_style' in report, "❌ Falta trading_style en reporte"
        assert report['trading_style'] == 'Day Trading', "❌ Estilo incorrecto en reporte"
        
        assert 'style_characteristics' in report, "❌ Falta style_characteristics en reporte"
        assert 'timeframe' in report['style_characteristics'], "❌ Falta timeframe en características"
        
        assert 'optimized_weights' in report, "❌ Falta optimized_weights en reporte"
        assert len(report['optimized_weights']) == 4, "❌ Número incorrecto de pesos"
        
        assert 'optimized_penalties' in report, "❌ Falta optimized_penalties en reporte"
        assert len(report['optimized_penalties']) >= 5, "❌ Número incorrecto de penalizaciones"
        
        assert 'data_statistics' in report, "❌ Falta data_statistics en reporte"
        assert len(report['data_statistics']) > 0, "❌ Estadísticas vacías"
        
        assert 'optimization_timestamp' in report, "❌ Falta optimization_timestamp en reporte"
        
        logger.info("✅ Reporte de optimización válido")
        logger.info(f"📊 Estilo: {report['trading_style']}")
        logger.info(f"📊 Pesos: {report['optimized_weights']}")
        logger.info(f"📊 Penalizaciones: {len(report['optimized_penalties'])} tipos")
        logger.info(f"📊 Estadísticas: {len(report['data_statistics'])} métricas")
        
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test de reporte: {e}")
        assert False

def test_gui_integration():
    """Test de integración con GUI."""
    
    logger.info("🧪 Iniciando test de integración con GUI")
    
    try:
        # Crear datos de prueba
        test_data = create_test_data_for_styles()
        df = test_data['Swing Trading']
        
        # Crear QVA Enhanced
        qva_enhanced = QVAScorerEnhanced()
        
        # Simular cambio de estilo desde GUI
        trading_style = 'Swing Trading'
        
        # Actualizar configuración desde GUI
        qva_enhanced.update_trading_style_from_gui(trading_style, df)
        
        # Verificar que se actualizaron los pesos
        current_weights = qva_enhanced.trading_style_weights.get(trading_style, {})
        assert len(current_weights) == 4, "❌ Pesos no actualizados correctamente"
        
        # Verificar que se actualizaron las penalizaciones
        assert len(qva_enhanced.penalty_config) >= 5, "❌ Penalizaciones no actualizadas correctamente"
        
        # Calcular scores con nueva configuración
        scores = qva_enhanced.calculate_qva_score(df)
        
        # Validaciones
        assert len(scores) == len(df), "❌ Número de scores incorrecto"
        assert scores.min() >= 0 and scores.max() <= 1, "❌ Rango de scores incorrecto"
        assert not scores.isnull().any(), "❌ Scores con valores nulos"
        
        logger.info("✅ Integración con GUI exitosa")
        logger.info(f"📊 Scores calculados: {len(scores)}")
        logger.info(f"📊 Rango de scores: [{scores.min():.4f}, {scores.max():.4f}]")
        
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test de integración GUI: {e}")
        assert False

def main():
    """Función principal para ejecutar todos los tests de automatización."""
    
    logger.info("🚀 Iniciando suite de tests de automatización QVA")
    
    tests = [
        ("Test de automatización por estilo", test_automation_by_trading_style),
        ("Test de reporte de optimización", test_optimization_report),
        ("Test de integración con GUI", test_gui_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            test_func()
            results.append((test_name, True))
            
            logger.info(f"✅ {test_name}: EXITOSO")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RESUMEN DE TESTS DE AUTOMATIZACIÓN")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ EXITOSO" if success else "❌ FALLÓ"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n📈 Resultado final: {passed}/{total} tests exitosos")
    
    if passed == total:
        logger.info("🎉 ¡Todos los tests de automatización pasaron exitosamente!")
        return True
    else:
        logger.error(f"❌ {total - passed} tests fallaron")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 