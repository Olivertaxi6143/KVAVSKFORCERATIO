#!/usr/bin/env python3
"""
Test para verificar las correcciones del market_regime_analyzer.py
"""

import sys
import os
import numpy as np
import pandas as pd
from typing import Dict, Any

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_market_regime_analyzer_import():
    """Test de importación del módulo corregido."""
    try:
        from core.market_regime_analyzer import HiddenMarkovModelAnalyzer
        print("✅ Importación exitosa de HiddenMarkovModelAnalyzer")
        assert True
    except Exception as e:
        print(f"❌ Error en importación: {e}")
        assert False

def test_hmm_analyzer_initialization():
    """Test de inicialización del analizador HMM."""
    try:
        from core.market_regime_analyzer import HiddenMarkovModelAnalyzer
        
        # Crear instancia
        analyzer = HiddenMarkovModelAnalyzer(n_states=3, random_state=42)
        
        # Verificar atributos
        assert analyzer.n_states == 3
        assert analyzer.random_state == 42
        assert analyzer.hmm_model is None
        assert analyzer.is_fitted is False
        
        print("✅ Inicialización exitosa del analizador HMM")
        assert True
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        assert False

def test_hmm_analyzer_fit():
    """Test del método fit_hmm."""
    try:
        from core.market_regime_analyzer import HiddenMarkovModelAnalyzer
        
        # Crear datos de prueba
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Crear datos sintéticos
        columns = [f'feature_{i}' for i in range(n_features)]
        data = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=pd.Index(columns)
        )
        
        # Crear analizador
        analyzer = HiddenMarkovModelAnalyzer(n_states=3, random_state=42)
        
        # Ajustar modelo
        result = analyzer.fit_hmm(data)
        
        # Verificar resultado
        assert isinstance(result, dict)
        assert 'regime_labels' in result
        assert 'regime_centroids' in result
        assert 'regime_characteristics' in result
        assert 'confidence_scores' in result
        assert 'transition_matrix' in result
        assert 'model' in result
        assert 'scaler' in result
        
        # Verificar que el modelo se guardó correctamente
        assert analyzer.is_fitted is True
        assert analyzer.hmm_model is not None
        assert isinstance(analyzer.hmm_model, dict)
        assert 'model' in analyzer.hmm_model
        assert 'scaler' in analyzer.hmm_model
        
        print("✅ Método fit_hmm funciona correctamente")
        assert True
    except Exception as e:
        print(f"❌ Error en fit_hmm: {e}")
        assert False

def test_hmm_analyzer_predict():
    """Test del método predict_regime."""
    try:
        from core.market_regime_analyzer import HiddenMarkovModelAnalyzer
        
        # Crear datos de prueba
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Crear datos sintéticos
        columns = [f'feature_{i}' for i in range(n_features)]
        data = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=pd.Index(columns)
        )
        
        # Crear analizador y ajustar
        analyzer = HiddenMarkovModelAnalyzer(n_states=3, random_state=42)
        analyzer.fit_hmm(data)
        
        # Crear datos de prueba para predicción
        test_data = np.random.randn(10, n_features)
        
        # Predecir
        regime_labels, regime_probs = analyzer.predict_regime(test_data)
        
        # Verificar resultados
        assert isinstance(regime_labels, np.ndarray)
        assert isinstance(regime_probs, np.ndarray)
        assert len(regime_labels) == 10
        assert regime_probs.shape[0] == 10
        assert regime_probs.shape[1] == 3  # 3 estados
        
        print("✅ Método predict_regime funciona correctamente")
        assert True
    except Exception as e:
        print(f"❌ Error en predict_regime: {e}")
        assert False

def test_characterize_regimes():
    """Test del método _characterize_regimes."""
    try:
        from core.market_regime_analyzer import HiddenMarkovModelAnalyzer
        
        # Crear analizador
        analyzer = HiddenMarkovModelAnalyzer(n_states=3, random_state=42)
        
        # Crear datos de prueba
        features = np.random.randn(100, 5)
        labels = np.random.randint(0, 3, 100)
        
        # Llamar al método
        characteristics = analyzer._characterize_regimes(features, labels)
        
        # Verificar resultado
        assert isinstance(characteristics, dict)
        assert len(characteristics) > 0
        
        print("✅ Método _characterize_regimes funciona correctamente")
        assert True
    except Exception as e:
        print(f"❌ Error en _characterize_regimes: {e}")
        assert False

def main():
    """Ejecutar todos los tests."""
    print("🧪 Ejecutando tests de correcciones del market_regime_analyzer...")
    print("=" * 60)
    
    tests = [
        test_market_regime_analyzer_import,
        test_hmm_analyzer_initialization,
        test_hmm_analyzer_fit,
        test_hmm_analyzer_predict,
        test_characterize_regimes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Error inesperado en {test.__name__}: {e}")
    
    print("=" * 60)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron! Las correcciones funcionan correctamente.")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisar las correcciones.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 