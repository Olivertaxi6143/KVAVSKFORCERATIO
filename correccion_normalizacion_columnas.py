#!/usr/bin/env python3
"""
Corrección para el problema de normalización de columnas.
El problema es que el Core Engine espera 'Strategy_Name' pero el CSV tiene 'Strategy Name'.
"""

import sys
import os
import pandas as pd

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def corregir_normalizacion_columnas():
    """Corrección para el problema de normalización de columnas."""
    
    print("🔧 APLICANDO CORRECCIÓN DE NORMALIZACIÓN DE COLUMNAS")
    print("=" * 60)
    
    # PASO 1: Verificar el problema
    print("\n1️⃣ Verificando el problema...")
    kpi_file = "DatabankExport_M1.csv"
    df = pd.read_csv(kpi_file, sep=';', decimal=',')
    
    print(f"📊 Datos originales: {len(df)} filas, {len(df.columns)} columnas")
    print(f"📋 Columnas originales: {list(df.columns)[:5]}...")
    
    # Verificar si existe la columna Strategy Name
    if 'Strategy Name' in df.columns:
        print("✅ Columna 'Strategy Name' encontrada")
    else:
        print("❌ Columna 'Strategy Name' no encontrada")
        return False
    
    # PASO 2: Aplicar corrección manual
    print("\n2️⃣ Aplicando corrección manual...")
    
    # Crear una copia del DataFrame
    df_corregido = df.copy()
    
    # Mapeo de columnas críticas
    mapeo_columnas = {
        'Strategy Name': 'Strategy_Name',
        'Profit factor': 'Profit_factor',
        'Sharpe Ratio': 'Sharpe_Ratio',
        'Drawdown': 'Drawdown',
        'Max DD %': 'Max_DD_%',
        'CAGR': 'CAGR',
        'CalmarRatio': 'CalmarRatio',
        'Expectancy': 'Expectancy',
        'Winning Percent': 'Winning_Percent',
        'Max Consec. Losses': 'Max_Consec_Losses',
        'RINAIndex': 'RINAIndex',
        'Ulcer Index %': 'Ulcer_Index_%',
        'RecoveryFactor': 'RecoveryFactor',
        'SQN': 'SQN',
        'Stagnation': 'Stagnation',
        'Max Drawdown Duration': 'Max_Drawdown_Duration',
        'Avg. Bars in Trade': 'Avg_Bars_in_Trade',
        'VaR (95%)': 'VaR_95%',
        'CVaR (95%)': 'CVaR_95%',
        'Sortino Ratio': 'Sortino_Ratio',
        'New Peak Trades %': 'New_Peak_Trades_%',
        'Drawdown Trades %': 'Drawdown_Trades_%'
    }
    
    # Aplicar mapeo
    columnas_renombradas = {}
    for col_original, col_nuevo in mapeo_columnas.items():
        if col_original in df_corregido.columns:
            df_corregido = df_corregido.rename(columns={col_original: col_nuevo})
            columnas_renombradas[col_original] = col_nuevo
            print(f"🔄 Renombrado: '{col_original}' -> '{col_nuevo}'")
    
    print(f"✅ Total de columnas renombradas: {len(columnas_renombradas)}")
    
    # Verificar que Strategy_Name existe
    if 'Strategy_Name' in df_corregido.columns:
        print("✅ Columna 'Strategy_Name' creada correctamente")
    else:
        print("❌ ERROR: No se pudo crear la columna 'Strategy_Name'")
        return False
    
    # PASO 3: Test con Core Engine
    print("\n3️⃣ Probando con Core Engine...")
    
    try:
        from src.core.integration_layer import FactorKElite96Enhanced
        
        config = {
            "trading_style": "General",
            "alpha": 0.8,
            "min_trades_monthly": 10,
            "percentil": 80,
            "scientific_improvements": True,
            "is_oos_split": 0.75
        }
        
        factor_k = FactorKElite96Enhanced(config)
        factor_k.enable_scientific_improvements()
        
        # Evaluar estrategias con datos corregidos
        df_result = factor_k.evaluate_strategies(df_corregido)
        
        print(f"✅ Core Engine: {len(df_result)} filas, {len(df_result.columns)} columnas")
        
        if df_result.empty:
            print("❌ PROBLEMA PERSISTE: Core Engine devolvió DataFrame vacío")
            return False
        else:
            print("✅ CORRECCIÓN EXITOSA: Core Engine funcionó correctamente")
            
            # Verificar columnas de score
            score_columns = [col for col in df_result.columns if 'Score' in col or 'FK96' in col]
            print(f"📊 Columnas de score: {score_columns}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR en Core Engine: {e}")
        import traceback
        traceback.print_exc()
        return False

def aplicar_correccion_permanente():
    """Aplicar corrección permanente en el DataLoaderEnhanced."""
    
    print("\n🔧 APLICANDO CORRECCIÓN PERMANENTE")
    print("=" * 60)
    
    # Leer el archivo DataLoaderEnhanced
    data_loader_file = "src/core/integration_layer.py"
    
    try:
        with open(data_loader_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la función _ensure_critical_columns
        if '_ensure_critical_columns' in content:
            print("✅ Función _ensure_critical_columns encontrada")
            
            # Verificar si ya tiene el mapeo correcto
            if "'Strategy Name'" in content:
                print("✅ Mapeo de 'Strategy Name' ya existe")
            else:
                print("⚠️ Mapeo de 'Strategy Name' no encontrado, agregando...")
                
                # Agregar el mapeo de Strategy Name
                old_mapping = "critical_mappings = {"
                new_mapping = """critical_mappings = {
                'Strategy_Name': ['Strategy Name', 'StrategyName', 'Name', 'Strategy'],"""
                
                if old_mapping in content:
                    content = content.replace(old_mapping, new_mapping)
                    
                    # Guardar el archivo corregido
                    with open(data_loader_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print("✅ Corrección aplicada permanentemente")
                else:
                    print("❌ No se pudo aplicar la corrección automática")
                    return False
        else:
            print("❌ Función _ensure_critical_columns no encontrada")
            return False
            
    except Exception as e:
        print(f"❌ ERROR aplicando corrección permanente: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO CORRECCIÓN DE NORMALIZACIÓN DE COLUMNAS")
    print("=" * 80)
    
    # Test de corrección manual
    success_manual = corregir_normalizacion_columnas()
    
    # Aplicar corrección permanente
    success_permanent = aplicar_correccion_permanente()
    
    print("\n📊 RESUMEN DE CORRECCIÓN")
    print("-" * 50)
    print(f"Corrección manual: {'✅ EXITOSA' if success_manual else '❌ FALLÓ'}")
    print(f"Corrección permanente: {'✅ EXITOSA' if success_permanent else '❌ FALLÓ'}")
    
    if success_manual and success_permanent:
        print("\n🎉 CORRECCIÓN COMPLETADA EXITOSAMENTE")
        print("✅ El problema de normalización de columnas ha sido resuelto")
    else:
        print("\n❌ ALGUNAS CORRECCIONES FALLARON")
        print("⚠️ Revisar logs para detalles") 