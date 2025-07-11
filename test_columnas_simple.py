#!/usr/bin/env python3
"""
TEST_COLUMNAS_SIMPLE.py - Verificar nombres de columnas
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import re

def test_columnas():
    """Test simple para verificar nombres de columnas."""
    print("🔍 TEST: Verificando nombres de columnas")
    print("=" * 50)
    
    # 1. Leer CSV original
    print("📊 Paso 1: Leyendo CSV original...")
    df_original = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
    print(f"✅ CSV cargado: {len(df_original)} filas, {len(df_original.columns)} columnas")
    print(f"📋 Columnas originales:")
    for i, col in enumerate(df_original.columns, 1):
        print(f"  {i:2d}. '{col}'")
    
    # 2. Simular normalización del DataManager
    print("\n🔄 Paso 2: Simulando normalización del DataManager...")
    
    def normalize_column_name(col):
        """Simula la normalización del DataManager."""
        # Reemplazar espacios y caracteres especiales con guiones bajos
        normalized = re.sub(r'[^a-zA-Z0-9_]', '_', col)
        # Remover guiones bajos múltiples
        normalized = re.sub(r'_+', '_', normalized)
        # Remover guiones bajos al inicio y final
        normalized = normalized.strip('_')
        return normalized
    
    df_normalizado = df_original.copy()
    df_normalizado.columns = [normalize_column_name(col) for col in df_original.columns]
    
    print("📋 Columnas normalizadas:")
    for i, (original, normalizada) in enumerate(zip(df_original.columns, df_normalizado.columns), 1):
        print(f"  {i:2d}. '{original}' → '{normalizada}'")
    
    # 3. Verificar KPIs específicos
    print("\n🎯 Paso 3: Verificando KPIs específicos...")
    
    kpis_buscar = [
        'CAGR (IS)', 'CAGR (OOS)', 
        'Sharpe Ratio (IS)', 'Sharpe Ratio (OOS)',
        'Sortino Ratio', 'SQN Score (IS)', 'SQN Score (OOS)',
        'Drawdown (IS)', 'Drawdown (OOS)',
        'Profit factor (IS)', 'Profit factor (OOS)',
        'RecoveryFactor'
    ]
    
    print("🔍 Buscando KPIs específicos:")
    for kpi in kpis_buscar:
        normalizado = normalize_column_name(kpi)
        encontrado_original = kpi in df_original.columns
        encontrado_normalizado = normalizado in df_normalizado.columns
        
        print(f"  • '{kpi}' → '{normalizado}'")
        print(f"    Original: {'✅' if encontrado_original else '❌'}")
        print(f"    Normalizado: {'✅' if encontrado_normalizado else '❌'}")
    
    # 4. Verificar KPIs numéricos disponibles
    print("\n🔢 Paso 4: Verificando KPIs numéricos...")
    
    kpis_numericos = []
    for col in df_normalizado.columns:
        if pd.api.types.is_numeric_dtype(df_normalizado[col]):
            kpis_numericos.append(col)
    
    print(f"📊 Total KPIs numéricos: {len(kpis_numericos)}")
    print("📋 KPIs numéricos disponibles:")
    for i, kpi in enumerate(kpis_numericos, 1):
        print(f"  {i:2d}. '{kpi}'")
    
    print("\n" + "=" * 50)
    print("✅ Test completado")

if __name__ == "__main__":
    test_columnas() 