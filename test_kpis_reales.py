#!/usr/bin/env python3
"""
Test simple para contar KPIs numéricos reales en DatabankExport_M1.csv
"""

import pandas as pd
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def contar_kpis_reales():
    """Cuenta los KPIs numéricos reales en el archivo DatabankExport_M1.csv."""
    
    print("🔍 CONTANDO KPIs NUMÉRICOS REALES")
    print("=" * 50)
    
    try:
        # Cargar el archivo directamente con separador correcto
        print("📂 Cargando DatabankExport_M1.csv...")
        df = pd.read_csv("DatabankExport_M1.csv", sep=';')
        
        print(f"📊 Archivo cargado: {len(df)} filas, {len(df.columns)} columnas")
        print(f"📋 Columnas disponibles: {list(df.columns)}")
        
        # Identificar columnas numéricas
        columnas_numericas = []
        columnas_no_numericas = []
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                columnas_numericas.append(col)
            else:
                columnas_no_numericas.append(col)
        
        print(f"\n📊 RESULTADOS:")
        print(f"✅ KPIs numéricos: {len(columnas_numericas)}")
        print(f"❌ Columnas no numéricas: {len(columnas_no_numericas)}")
        
        print(f"\n📋 KPIs NUMÉRICOS DETECTADOS ({len(columnas_numericas)}):")
        print("-" * 50)
        for i, kpi in enumerate(columnas_numericas, 1):
            print(f"{i:2d}. {kpi}")
        
        print(f"\n📋 COLUMNAS NO NUMÉRICAS ({len(columnas_no_numericas)}):")
        print("-" * 50)
        for i, col in enumerate(columnas_no_numericas, 1):
            print(f"{i:2d}. {col}")
        
        # Mostrar estadísticas de algunos KPIs importantes
        print(f"\n📈 ESTADÍSTICAS DE KPIs IMPORTANTES:")
        print("-" * 50)
        kpis_importantes = ['CAGR', 'Profit_factor', 'Sharpe_Ratio', 'Drawdown', 'Winning_Percent']
        for kpi in kpis_importantes:
            if kpi in columnas_numericas:
                stats = df[kpi].describe()
                print(f"{kpi}:")
                print(f"  • Min: {stats['min']:.4f}")
                print(f"  • Max: {stats['max']:.4f}")
                print(f"  • Mean: {stats['mean']:.4f}")
                print(f"  • Std: {stats['std']:.4f}")
                print()
        
        return len(columnas_numericas), columnas_numericas
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 0, []

if __name__ == "__main__":
    num_kpis, kpis_list = contar_kpis_reales()
    print(f"\n🎯 TOTAL KPIs NUMÉRICOS ENCONTRADOS: {num_kpis}") 