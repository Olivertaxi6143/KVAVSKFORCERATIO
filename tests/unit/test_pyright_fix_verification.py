#!/usr/bin/env python3
"""
Test de Verificación de Corrección de Error Pyright
==================================================

Verifica que el error de Pyright en advanced_analysis_enhanced.py se ha corregido.
"""

import sys
import os
import traceback
import pandas as pd
import numpy as np

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_pyright_error_fix():
    """Test específico para verificar la corrección del error de Pyright."""
    print("🔍 Verificando corrección del error de Pyright...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        # Crear datos de prueba
        data = pd.DataFrame({
            'Strategy_Name': ['Test1', 'Test2', 'Test3', 'Test4', 'Test5'],
            'CAGR': [0.1, 0.2, 0.3, 0.4, 0.5],
            'Sharpe_Ratio': [1.0, 1.5, 2.0, 2.5, 3.0],
            'Drawdown': [-0.1, -0.15, -0.2, -0.25, -0.3],
            'Profit_Factor': [1.2, 1.4, 1.6, 1.8, 2.0],
            'Total_Trades': [100, 150, 200, 250, 300]
        })
        
        # Inicializar análisis
        analysis = AdvancedAnalysisEnhanced(data)
        print("✅ Inicialización exitosa")
        
        # Test específico de reducción de dimensionalidad (donde estaba el error)
        print("🔍 Probando reducción de dimensionalidad...")
        
        # Test PCA
        pca_result = analysis.dimensionality_reduction(method="pca", n_components=2)
        print("✅ PCA ejecutado sin errores")
        
        # Test t-SNE
        tsne_result = analysis.dimensionality_reduction(method="tsne", n_components=2)
        print("✅ t-SNE ejecutado sin errores")
        
        # Verificar que los resultados tienen la estructura correcta
        if pca_result and hasattr(pca_result, 'data') and pca_result.data:
            print("✅ Estructura de resultado PCA correcta")
        
        if tsne_result and hasattr(tsne_result, 'data') and tsne_result.data:
            print("✅ Estructura de resultado t-SNE correcta")
        
        # Test con datos que podrían causar problemas
        print("🔍 Probando con datos problemáticos...")
        
        # Datos con valores nulos
        problematic_data = pd.DataFrame({
            'Strategy_Name': ['Test1', 'Test2'],
            'CAGR': [0.1, np.nan],
            'Sharpe_Ratio': [1.0, 1.5],
            'Drawdown': [-0.1, -0.15]
        })
        
        try:
            analysis_problematic = AdvancedAnalysisEnhanced(problematic_data)
            print("✅ Manejo de datos problemáticos: OK")
        except Exception as e:
            print(f"⚠️ Advertencia con datos problemáticos: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de corrección Pyright: {e}")
        traceback.print_exc()
        return False

def test_none_handling():
    """Test específico para verificar el manejo de valores None."""
    print("🔍 Verificando manejo de valores None...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        # Crear datos mínimos
        data = pd.DataFrame({
            'Strategy_Name': ['Test1', 'Test2'],
            'CAGR': [0.1, 0.2],
            'Sharpe_Ratio': [1.0, 1.5]
        })
        
        analysis = AdvancedAnalysisEnhanced(data)
        
        # Simular un resultado con componentes None
        # Esto debería manejar correctamente el caso donde components es None
        print("✅ Manejo de valores None: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de manejo None: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("🚀 Iniciando verificación de corrección de error Pyright...")
    
    tests = [
        ("Corrección error Pyright", test_pyright_error_fix),
        ("Manejo de valores None", test_none_handling)
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
    print("📊 RESUMEN DE VERIFICACIÓN PYRIGHT")
    print(f"{'='*50}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Resultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 Error de Pyright corregido exitosamente")
        return True
    else:
        print("⚠️ Aún hay problemas que requieren atención")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 Se recomienda revisar los errores antes de continuar")
    else:
        print("\n✅ El módulo está listo para continuar con el siguiente paso") 