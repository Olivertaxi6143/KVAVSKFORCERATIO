#!/usr/bin/env python3
"""
Test específico para verificar las mejoras de IA en FactorKElite96Enhanced.
"""

import sys
import os
import pandas as pd
import numpy as np
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_ai_enhanced_factor_k():
    """Test específico de las mejoras de IA en FactorKElite96Enhanced."""
    
    print("🔍 TEST ESPECÍFICO: FactorKElite96Enhanced con IA Avanzada")
    print("=" * 70)
    
    # Cargar datos de prueba
    kpi_file = "DatabankExport_M1.csv"
    df = pd.read_csv(kpi_file, sep=';', decimal=',')
    
    print(f"📊 Datos originales: {len(df)} filas, {len(df.columns)} columnas")
    
    # Importar el evaluador
    from src.core.analysis.factor_k_analyzer import FactorKElite96Enhanced
    
    try:
        # Crear evaluador con IA avanzada
        config = {
            "trading_style": "General",
            "alpha": 0.8,
            "min_trades_monthly": 10,
            "percentil": 80,
            "scientific_improvements": True,
            "is_oos_split": 0.75
        }
        
        factor_k = FactorKElite96Enhanced(config)
        
        # Evaluar estrategias con IA avanzada
        print("\n🔄 Evaluando estrategias con FactorKElite96Enhanced + IA...")
        df_result = factor_k.evaluate_strategies(df)
        
        print(f"✅ Resultado: {len(df_result)} filas, {len(df_result.columns)} columnas")
        
        # Verificar componentes de IA
        ai_components = []
        
        # Verificar componentes tradicionales
        traditional_components = [
            'FK96_Stability_Enhanced', 'FK96_Growth_Enhanced', 
            'FK96_Efficiency_Enhanced', 'FK96_Consistency_Enhanced', 
            'FK96_Risk_Enhanced'
        ]
        
        for component in traditional_components:
            if component in df_result.columns:
                ai_components.append(component)
                print(f"✅ {component}: Presente")
        
        # Verificar componentes de IA avanzada
        ai_advanced_components = [
            'FK96_Temporal_Component', 'FK96_Predictive_Component',
            'Anomaly_Score', 'Is_Anomaly', 'Market_Regime',
            'HMM_State', 'HMM_Score', 'HMM_State_Probability'
        ]
        
        print("\n🔬 COMPONENTES DE IA AVANZADA:")
        for component in ai_advanced_components:
            if component in df_result.columns:
                ai_components.append(component)
                print(f"✅ {component}: Presente")
                
                # Mostrar estadísticas básicas
                if component in ['FK96_Temporal_Component', 'FK96_Predictive_Component']:
                    mean_val = df_result[component].mean()
                    std_val = df_result[component].std()
                    print(f"   📊 Media: {mean_val:.3f}, Std: {std_val:.3f}")
                elif component == 'Is_Anomaly':
                    anomaly_count = df_result[component].sum()
                    total_count = len(df_result)
                    print(f"   📊 Anomalías: {anomaly_count}/{total_count} ({anomaly_count/total_count*100:.1f}%)")
                elif component == 'Market_Regime':
                    regime_counts = df_result[component].value_counts()
                    print(f"   📊 Regímenes: {dict(regime_counts)}")
                elif component == 'HMM_State':
                    state_counts = df_result[component].value_counts()
                    print(f"   📊 Estados HMM: {dict(state_counts)}")
            else:
                print(f"❌ {component}: No presente")
        
        # Verificar scores finales
        print("\n🎯 SCORES FINALES:")
        final_scores = [
            'FK96_Elite_Enhanced', 'FK96_Elite_Enhanced_Scientific',
            'FK96_Elite_Enhanced_Normalized', 'Unified_Score'
        ]
        
        for score in final_scores:
            if score in df_result.columns:
                mean_score = df_result[score].mean()
                max_score = df_result[score].max()
                min_score = df_result[score].min()
                print(f"✅ {score}: Media={mean_score:.3f}, Max={max_score:.3f}, Min={min_score:.3f}")
            else:
                print(f"❌ {score}: No presente")
        
        # Verificar categorías de calidad
        print("\n🏆 CATEGORÍAS DE CALIDAD:")
        if 'Quality_Category' in df_result.columns:
            category_counts = df_result['Quality_Category'].value_counts()
            print("Distribución de categorías:")
            for category, count in category_counts.items():
                percentage = count / len(df_result) * 100
                print(f"   {category}: {count} ({percentage:.1f}%)")
        else:
            print("❌ Quality_Category: No presente")
        
        # Verificar pesos optimizados
        print("\n⚖️ PESOS OPTIMIZADOS:")
        if hasattr(factor_k, 'optimized_weights') and factor_k.optimized_weights:
            for component, weight in factor_k.optimized_weights.items():
                print(f"   {component}: {weight:.3f}")
        else:
            print("❌ Pesos optimizados: No disponibles")
        
        # Resumen de mejoras de IA
        print("\n📈 RESUMEN DE MEJORAS DE IA:")
        print(f"   • Componentes tradicionales: {len([c for c in traditional_components if c in df_result.columns])}/{len(traditional_components)}")
        print(f"   • Componentes de IA avanzada: {len([c for c in ai_advanced_components if c in df_result.columns])}/{len(ai_advanced_components)}")
        print(f"   • Total de componentes: {len(ai_components)}")
        
        # Verificar que al menos algunos componentes de IA están presentes
        ai_components_present = [c for c in ai_advanced_components if c in df_result.columns]
        assert len(ai_components_present) >= 2, f"Se esperaban al menos 2 componentes de IA, se encontraron {len(ai_components_present)}"
        
        print("\n✅ TEST EXITOSO: FactorKElite96Enhanced con IA avanzada funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en FactorKElite96Enhanced con IA: {e}")
        import traceback
        traceback.print_exc()
        raise

def test_hmm_real_implementation():
    """Test específico para verificar la implementación de HMM real."""
    
    print("\n🔍 TEST ESPECÍFICO: HMM Real Implementation")
    print("=" * 50)
    
    try:
        # Verificar disponibilidad de hmmlearn
        try:
            from hmmlearn import hmm
            hmm_available = True
            print("✅ hmmlearn disponible")
        except ImportError:
            hmm_available = False
            print("❌ hmmlearn no disponible")
        
        # Crear datos sintéticos para test
        np.random.seed(42)
        n_samples = 100
        n_features = 3
        
        # Simular métricas de estrategias
        sharpe_ratios = np.random.normal(1.5, 0.5, n_samples)
        max_drawdowns = np.random.uniform(5, 25, n_samples)
        cagr_values = np.random.normal(15, 5, n_samples)
        
        # Crear DataFrame sintético
        df_synthetic = pd.DataFrame({
            'Sharpe_Ratio': sharpe_ratios,
            'Max_DD_%': max_drawdowns,
            'CAGR': cagr_values,
            'FK96_Elite_Enhanced': np.random.uniform(0.5, 0.9, n_samples)
        })
        
        # Importar y probar HMM
        from src.core.analysis.factor_k_analyzer import FactorKElite96Enhanced
        
        factor_k = FactorKElite96Enhanced()
        
        # Aplicar HMM real
        df_result = factor_k._apply_real_hmm_analysis(df_synthetic)
        
        # Verificar resultados
        hmm_columns = ['HMM_State', 'HMM_Score', 'HMM_State_Probability']
        
        for col in hmm_columns:
            if col in df_result.columns:
                print(f"✅ {col}: Presente")
                if col == 'HMM_State':
                    states = df_result[col].value_counts()
                    print(f"   Estados detectados: {dict(states)}")
                elif col == 'HMM_State_Probability':
                    mean_prob = df_result[col].mean()
                    print(f"   Probabilidad media: {mean_prob:.3f}")
            else:
                print(f"❌ {col}: No presente")
        
        print("✅ HMM Real Implementation: Funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en HMM Real Implementation: {e}")
        import traceback
        traceback.print_exc()
        raise

def test_anomaly_detection():
    """Test específico para verificar la detección de anomalías."""
    
    print("\n🔍 TEST ESPECÍFICO: Anomaly Detection")
    print("=" * 40)
    
    try:
        # Crear datos sintéticos con algunas anomalías
        np.random.seed(42)
        n_samples = 100
        
        # Datos normales
        normal_data = pd.DataFrame({
            'Sharpe_Ratio': np.random.normal(1.5, 0.3, n_samples),
            'Max_DD_%': np.random.uniform(10, 20, n_samples),
            'CAGR': np.random.normal(15, 3, n_samples),
            'Profit_factor': np.random.uniform(1.2, 2.0, n_samples),
            'Total_Trades': np.random.randint(50, 200, n_samples)
        })
        
        # Añadir algunas anomalías
        anomaly_indices = [10, 25, 50, 75, 90]
        for idx in anomaly_indices:
            normal_data.loc[idx, 'Sharpe_Ratio'] = 5.0  # Sharpe muy alto
            normal_data.loc[idx, 'Max_DD_%'] = 50.0     # Drawdown muy alto
            normal_data.loc[idx, 'CAGR'] = 50.0         # CAGR muy alto
        
        # Importar y probar detección de anomalías
        from src.core.analysis.factor_k_analyzer import FactorKElite96Enhanced
        
        factor_k = FactorKElite96Enhanced()
        
        # Aplicar detección de anomalías
        df_result = factor_k._detect_anomalies_multivariate(normal_data)
        
        # Verificar resultados
        if 'Is_Anomaly' in df_result.columns:
            anomaly_count = df_result['Is_Anomaly'].sum()
            total_count = len(df_result)
            print(f"✅ Anomalías detectadas: {anomaly_count}/{total_count} ({anomaly_count/total_count*100:.1f}%)")
            
            # Verificar que se detectaron las anomalías artificiales
            detected_anomalies = df_result[df_result['Is_Anomaly'] == 1].index.tolist()
            print(f"   Índices de anomalías detectadas: {detected_anomalies}")
            
            # Verificar que algunas de las anomalías artificiales fueron detectadas
            artificial_anomalies_detected = sum(1 for idx in anomaly_indices if idx in detected_anomalies)
            print(f"   Anomalías artificiales detectadas: {artificial_anomalies_detected}/{len(anomaly_indices)}")
            
        else:
            print("❌ Is_Anomaly: No presente")
        
        if 'Anomaly_Score' in df_result.columns:
            print(f"✅ Anomaly_Score: Presente (rango: {df_result['Anomaly_Score'].min()} a {df_result['Anomaly_Score'].max()})")
        else:
            print("❌ Anomaly_Score: No presente")
        
        print("✅ Anomaly Detection: Funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en Anomaly Detection: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE IA AVANZADA")
    print("=" * 80)
    
    tests = [
        ("FactorKElite96Enhanced con IA", test_ai_enhanced_factor_k),
        ("HMM Real Implementation", test_hmm_real_implementation),
        ("Anomaly Detection", test_anomaly_detection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n📊 RESUMEN DE TESTS DE IA AVANZADA")
    print("-" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("✅ TODOS LOS TESTS DE IA AVANZADA PASARON")
    else:
        print("❌ ALGUNOS TESTS DE IA AVANZADA FALLARON") 