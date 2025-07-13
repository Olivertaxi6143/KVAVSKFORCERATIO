#!/usr/bin/env python3
"""
Test simple para verificar helpers de seguridad.
"""

import sys
import os
import pandas as pd
import numpy as np

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_safe_len_simple():
    """Test simple de safe_len."""
    print("🧪 Test simple de safe_len")
    
    try:
        from src.core.predictability_analyzer import safe_len
        
        # Test básico
        test_list = [1, 2, 3, 4, 5]
        result = safe_len(test_list)
        print(f"✅ safe_len([1,2,3,4,5]) = {result}")
        
        # Test con None
        result = safe_len(None)
        print(f"✅ safe_len(None) = {result}")
        
        # Test con Series
        test_series = pd.Series([1, 2, 3])
        result = safe_len(test_series)
        print(f"✅ safe_len(Series) = {result}")
        
        print("✅ Test simple PASÓ")
        return True
        
    except Exception as e:
        print(f"❌ Error en test simple: {e}")
        return False

def test_safe_getitem_simple():
    """Test simple de safe_getitem."""
    print("🧪 Test simple de safe_getitem")
    
    try:
        from src.core.predictability_analyzer import safe_getitem
        
        # Test básico
        test_list = [10, 20, 30, 40, 50]
        result = safe_getitem(test_list, 2)
        print(f"✅ safe_getitem([10,20,30,40,50], 2) = {result}")
        
        # Test con índice fuera de rango
        result = safe_getitem(test_list, 10)
        print(f"✅ safe_getitem([10,20,30,40,50], 10) = {result}")
        
        # Test con None
        result = safe_getitem(None, 0)
        print(f"✅ safe_getitem(None, 0) = {result}")
        
        print("✅ Test simple PASÓ")
        return True
        
    except Exception as e:
        print(f"❌ Error en test simple: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("🧪 TESTS SIMPLES DE HELPERS DE SEGURIDAD")
    print("="*50)
    
    test1_passed = test_safe_len_simple()
    test2_passed = test_safe_getitem_simple()
    
    print("="*50)
    if test1_passed and test2_passed:
        print("🎉 TODOS LOS TESTS SIMPLES PASARON")
    else:
        print("❌ ALGUNOS TESTS SIMPLES FALLARON")
    print("="*50) 