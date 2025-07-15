#!/usr/bin/env python3
"""
Test Rápido de Verificación de Errores
======================================

Verifica errores específicos comunes en AdvancedAnalysisEnhanced.
"""

import sys
import os
import traceback

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test de importaciones."""
    print("🔍 Verificando importaciones...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced, AnalysisType
        print("✅ Importaciones principales: OK")
        
        # Verificar imports internos
        from sklearn.cluster import KMeans, DBSCAN
        from sklearn.ensemble import IsolationForest
        from sklearn.neighbors import LocalOutlierFactor
        from sklearn.covariance import EllipticEnvelope
        from sklearn.mixture import GaussianMixture
        from sklearn.manifold import TSNE
        from sklearn.decomposition import PCA
        print("✅ Imports de scikit-learn: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test de funcionalidad básica."""
    print("🔍 Verificando funcionalidad básica...")
    
    try:
        import pandas as pd
        import numpy as np
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        # Crear datos mínimos
        data = pd.DataFrame({
            'Strategy_Name': ['Test1', 'Test2', 'Test3'],
            'CAGR': [0.1, 0.2, 0.3],
            'Sharpe_Ratio': [1.0, 1.5, 2.0],
            'Drawdown': [-0.1, -0.15, -0.2]
        })
        
        # Inicializar
        analysis = AdvancedAnalysisEnhanced(data)
        print("✅ Inicialización: OK")
        
        # Test método básico
        result = analysis.regime_analysis(method="kmeans", n_regimes=2)
        print("✅ Análisis de regímenes: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test de manejo de errores."""
    print("🔍 Verificando manejo de errores...")
    
    try:
        import pandas as pd
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        # Test con datos vacíos
        empty_data = pd.DataFrame()
        try:
            analysis = AdvancedAnalysisEnhanced(empty_data)
            print("⚠️ Advertencia: Debería fallar con datos vacíos")
        except Exception:
            print("✅ Manejo de datos vacíos: OK")
        
        # Test con datos mínimos
        minimal_data = pd.DataFrame({
            'Strategy_Name': ['Test1'],
            'CAGR': [0.1]
        })
        
        try:
            analysis = AdvancedAnalysisEnhanced(minimal_data)
            print("✅ Manejo de datos mínimos: OK")
        except Exception as e:
            print(f"❌ Error con datos mínimos: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de manejo de errores: {e}")
        traceback.print_exc()
        return False

def test_type_safety():
    """Test de seguridad de tipos."""
    print("🔍 Verificando seguridad de tipos...")
    
    try:
        import pandas as pd
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        # Test con tipos mixtos
        mixed_data = pd.DataFrame({
            'Strategy_Name': ['Test1', 'Test2'],
            'CAGR': [0.1, 'invalid'],  # Tipo mixto
            'Sharpe_Ratio': [1.0, 1.5]
        })
        
        try:
            analysis = AdvancedAnalysisEnhanced(mixed_data)
            print("✅ Manejo de tipos mixtos: OK")
        except Exception as e:
            print(f"⚠️ Advertencia con tipos mixtos: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de tipos: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("🚀 Iniciando verificación rápida de errores...")
    
    tests = [
        ("Importaciones", test_imports),
        ("Funcionalidad básica", test_basic_functionality),
        ("Manejo de errores", test_error_handling),
        ("Seguridad de tipos", test_type_safety)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🔬 {test_name}")
        print(f"{'='*50}")
        
        try:
            success = test_func()
            results[test_name] = success
            status = "✅ PASÓ" if success else "❌ FALLÓ"
            print(f"{test_name}: {status}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR CRÍTICO - {e}")
            results[test_name] = False
    
    # Resumen
    print(f"\n{'='*50}")
    print("📊 RESUMEN DE VERIFICACIÓN RÁPIDA")
    print(f"{'='*50}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Resultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 Verificación rápida exitosa")
        return True
    else:
        print("⚠️ Se detectaron problemas que requieren atención")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 Se recomienda revisar los errores antes de continuar") 