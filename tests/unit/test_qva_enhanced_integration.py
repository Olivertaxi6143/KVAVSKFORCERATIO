#!/usr/bin/env python3
"""
Test de integración para QVAScorerEnhanced con DataManager

Valida que el QVA Enhanced funcione correctamente con:
- Datos reales de INPUTTEST
- Integración con DataManager
- Componentes de ML (si están disponibles)
- Penalizaciones avanzadas
- Explicabilidad de scores
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
logger = setup_logger("test_qva_enhanced")

def test_qva_enhanced_integration():
    """Test principal de integración del QVA Enhanced."""
    
    logger.info("🧪 Iniciando test de integración QVA Enhanced")
    
    try:
        # 1. Crear DataManager y cargar datos
        logger.info("📊 Paso 1: Creando DataManager...")
        data_manager = create_data_manager()
        
        # Configurar para usar INPUTTEST
        data_manager.config['development']['use_inputtest'] = True
        
        # Cargar datos
        success = data_manager.load_all_data()
        logger.info(f"✅ Datos cargados: {'Exitoso' if success else 'Falló'}")
        
        # 2. Obtener datos para el test
        logger.info("📊 Paso 2: Obteniendo datos...")
        df = data_manager.get_data_for_core_engine()
        
        if df.empty:
            logger.error("❌ No hay datos disponibles para el test")
            assert False
        
        logger.info(f"✅ Datos obtenidos: {len(df)} registros, {len(df.columns)} columnas")
        logger.info(f"📋 Columnas disponibles: {list(df.columns)[:10]}...")
        
        # 3. Crear QVA Enhanced
        logger.info("🤖 Paso 3: Creando QVAScorerEnhanced...")
        config_manager = ConfigManagerEnhanced()
        qva_enhanced = QVAScorerEnhanced(
            config_manager=config_manager,
            data_manager=data_manager
        )
        
        # 4. Calcular scores QVA
        logger.info("🎯 Paso 4: Calculando scores QVA...")
        scores = qva_enhanced.calculate_qva_score(df)
        
        # 5. Validaciones básicas
        logger.info("✅ Paso 5: Validando resultados...")
        
        # Verificar que se calcularon scores
        assert len(scores) == len(df), f"❌ Número de scores ({len(scores)}) no coincide con datos ({len(df)})"
        logger.info(f"✅ Número de scores correcto: {len(scores)}")
        
        # Verificar rango de scores
        assert scores.min() >= 0 and scores.max() <= 1, f"❌ Scores fuera de rango [0,1]: min={scores.min()}, max={scores.max()}"
        logger.info(f"✅ Rango de scores correcto: [{scores.min():.4f}, {scores.max():.4f}]")
        
        # Verificar que no hay nulos
        assert not scores.isnull().any(), "❌ Scores contienen valores nulos"
        logger.info("✅ No hay valores nulos en scores")
        
        # 6. Verificar correlación con métricas objetivo
        logger.info("📈 Paso 6: Verificando correlaciones...")
        
        if 'CAGR' in df.columns:
            cagr_correlation = df['CAGR'].corr(scores)
            logger.info(f"📈 Correlación con CAGR: {cagr_correlation:.4f}")
            assert cagr_correlation > 0.1, f"❌ Correlación con CAGR muy baja: {cagr_correlation}"
        
        if 'Sharpe_Ratio' in df.columns:
            sharpe_correlation = df['Sharpe_Ratio'].corr(scores)
            logger.info(f"📈 Correlación con Sharpe: {sharpe_correlation:.4f}")
            assert sharpe_correlation > 0.1, f"❌ Correlación con Sharpe muy baja: {sharpe_correlation}"
        
        # 7. Obtener desglose de scores
        logger.info("🔍 Paso 7: Obteniendo desglose de scores...")
        breakdown = qva_enhanced.get_score_breakdown(df)
        
        assert 'profitability' in breakdown, "❌ Falta componente de rentabilidad"
        assert 'risk' in breakdown, "❌ Falta componente de riesgo"
        assert 'consistency' in breakdown, "❌ Falta componente de consistencia"
        assert 'ml_enhancement' in breakdown, "❌ Falta componente de ML"
        assert 'penalties' in breakdown, "❌ Falta componente de penalizaciones"
        
        logger.info("✅ Desglose de scores obtenido correctamente")
        
        # 8. Explicar score de una estrategia
        logger.info("💡 Paso 8: Explicando score de estrategia...")
        if len(df) > 0:
            explanation = qva_enhanced.explain_score(df, 0)
            logger.info(f"💡 Explicación de estrategia 0: {explanation}")
            assert len(explanation) > 0, "❌ No se pudo explicar el score"
        
        # 9. Estadísticas finales
        logger.info("📊 Paso 9: Estadísticas finales...")
        
        logger.info(f"📊 Estadísticas de scores:")
        logger.info(f"   - Media: {scores.mean():.4f}")
        logger.info(f"   - Desv. Est.: {scores.std():.4f}")
        logger.info(f"   - Mínimo: {scores.min():.4f}")
        logger.info(f"   - Máximo: {scores.max():.4f}")
        logger.info(f"   - Mediana: {scores.median():.4f}")
        
        # Top 5 estrategias
        top_5_idx = scores.nlargest(5).index
        logger.info(f"🏆 Top 5 estrategias:")
        for i, idx in enumerate(top_5_idx):
            strategy_name = df.iloc[idx].get('Strategy_Name', f'Strategy_{idx}')
            score = scores.iloc[idx]
            logger.info(f"   {i+1}. {strategy_name}: {score:.4f}")
        
        # 10. Verificar componentes de ML
        logger.info("🤖 Paso 10: Verificando componentes de ML...")
        
        # Verificar que el componente de ML se calculó
        ml_scores = breakdown.get('ml_enhancement', pd.Series())
        if not ml_scores.empty:
            logger.info(f"🤖 Componente ML: media={ml_scores.mean():.4f}, std={ml_scores.std():.4f}")
        else:
            logger.warning("⚠️ Componente ML no disponible")
        
        # 11. Verificar penalizaciones
        logger.info("⚠️ Paso 11: Verificando penalizaciones...")
        
        penalties = breakdown.get('penalties', pd.Series())
        if not penalties.empty:
            logger.info(f"⚠️ Penalizaciones: media={penalties.mean():.4f}, std={penalties.std():.4f}")
            logger.info(f"⚠️ Estrategias penalizadas: {(penalties < 1.0).sum()}/{len(penalties)}")
        else:
            logger.warning("⚠️ Penalizaciones no disponibles")
        
        logger.info("🎉 ¡Test de integración QVA Enhanced completado exitosamente!")
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test de integración: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        assert False

def test_qva_enhanced_with_real_data():
    """Test específico con datos reales de INPUTTEST."""
    
    logger.info("🧪 Iniciando test con datos reales")
    
    try:
        # Cargar datos directamente desde INPUTTEST
        inputtest_path = Path("INPUTTEST/DatabankExport_M1.csv")
        
        if not inputtest_path.exists():
            logger.error(f"❌ Archivo no encontrado: {inputtest_path}")
            assert False
        
        # Leer datos
        df = pd.read_csv(inputtest_path, sep=';', decimal=',')
        logger.info(f"✅ Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
        
        # Crear QVA Enhanced
        qva_enhanced = QVAScorerEnhanced()
        
        # Calcular scores
        scores = qva_enhanced.calculate_qva_score(df)
        
        # Validaciones
        assert len(scores) == len(df), "❌ Número de scores incorrecto"
        assert scores.min() >= 0 and scores.max() <= 1, "❌ Rango de scores incorrecto"
        assert not scores.isnull().any(), "❌ Scores con valores nulos"
        
        logger.info(f"✅ Test con datos reales exitoso: {len(scores)} scores calculados")
        logger.info(f"📊 Rango de scores: [{scores.min():.4f}, {scores.max():.4f}]")
        
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test con datos reales: {e}")
        assert False

def test_qva_enhanced_components():
    """Test de componentes individuales del QVA Enhanced."""
    
    logger.info("🧪 Iniciando test de componentes")
    
    try:
        # Crear datos de prueba
        test_data = {
            'Strategy_Name': [f'Strategy_{i}' for i in range(10)],
            'CAGR': np.random.uniform(1.0, 5.0, 10),
            'Sharpe_Ratio': np.random.uniform(0.5, 2.0, 10),
            'Profit_factor': np.random.uniform(1.1, 2.0, 10),
            'Drawdown': np.random.uniform(5.0, 20.0, 10),
            'Max_Consec_Losses': np.random.randint(3, 12, 10),
            'Stagnation': np.random.randint(5, 25, 10),
            'Exposure': np.random.uniform(0.2, 0.8, 10),
            'Winning_Percent': np.random.uniform(0.3, 0.7, 10),
            'CalmarRatio': np.random.uniform(0.5, 3.0, 10),
            'SQN': np.random.uniform(0.5, 2.0, 10)
        }
        
        df = pd.DataFrame(test_data)
        
        # Crear QVA Enhanced
        qva_enhanced = QVAScorerEnhanced()
        
        # Test de componentes individuales
        enabled_kpis = ['CAGR', 'Sharpe_Ratio', 'Profit_factor', 'Drawdown', 'CalmarRatio', 'SQN']
        
        # Test componente de rentabilidad
        profitability = qva_enhanced._calculate_profitability_component_enhanced(df, enabled_kpis)
        assert len(profitability) == len(df), "❌ Error en componente de rentabilidad"
        logger.info("✅ Componente de rentabilidad OK")
        
        # Test componente de riesgo
        risk = qva_enhanced._calculate_risk_component_enhanced(df, enabled_kpis)
        assert len(risk) == len(df), "❌ Error en componente de riesgo"
        logger.info("✅ Componente de riesgo OK")
        
        # Test componente de consistencia
        consistency = qva_enhanced._calculate_consistency_component_enhanced(df, enabled_kpis)
        assert len(consistency) == len(df), "❌ Error en componente de consistencia"
        logger.info("✅ Componente de consistencia OK")
        
        # Test componente de ML
        ml_enhancement = qva_enhanced._calculate_ml_enhancement_component(df)
        assert len(ml_enhancement) == len(df), "❌ Error en componente de ML"
        logger.info("✅ Componente de ML OK")
        
        # Test penalizaciones
        penalties = qva_enhanced._calculate_advanced_penalties_enhanced(df)
        assert 'total_penalty' in penalties, "❌ Error en penalizaciones"
        logger.info("✅ Penalizaciones OK")
        
        logger.info("🎉 Test de componentes completado exitosamente!")
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test de componentes: {e}")
        assert False

def main():
    """Función principal para ejecutar todos los tests."""
    
    logger.info("🚀 Iniciando suite de tests QVA Enhanced")
    
    tests = [
        ("Test de integración", test_qva_enhanced_integration),
        ("Test con datos reales", test_qva_enhanced_with_real_data),
        ("Test de componentes", test_qva_enhanced_components)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                logger.info(f"✅ {test_name}: EXITOSO")
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RESUMEN DE TESTS")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ EXITOSO" if success else "❌ FALLÓ"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n📈 Resultado final: {passed}/{total} tests exitosos")
    
    if passed == total:
        logger.info("🎉 ¡Todos los tests pasaron exitosamente!")
        return True
    else:
        logger.error(f"❌ {total - passed} tests fallaron")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 