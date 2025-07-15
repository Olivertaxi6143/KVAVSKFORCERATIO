import sys
import os
import pandas as pd
import traceback
from src.data.data_manager import DataManager
from src.core.integration_layer import run_complete_analysis_with_gui_integration

# Rutas de entrada/salida en INPUTTEST
kpi_path = "INPUTTEST/DatabankExport_M1.csv"
output_path = "INPUTTEST/cli_analysis_results.csv"

try:
    print('[TEST] Cargando archivo KPI...')
    df_kpi = pd.read_csv(kpi_path, sep=';', quotechar='"', engine='python')
    print(f"[TEST] Columnas leídas: {list(df_kpi.columns)}")
    columnas_requeridas = ['Strategy Name', 'CAGR', 'Drawdown', 'Profit factor']
    faltantes = [col for col in columnas_requeridas if col not in df_kpi.columns]
    if faltantes:
        print(f"[TEST][ERROR] Faltan columnas requeridas en el archivo KPI: {faltantes}")
        sys.exit(1)
    print(f"[TEST] Archivo KPI cargado correctamente: {df_kpi.shape}")

    # Normalizar nombre de columna para compatibilidad con el core
    if 'Strategy Name' in df_kpi.columns:
        df_kpi = df_kpi.rename(columns={'Strategy Name': 'Strategy_Name'})
        print("[TEST] Columna 'Strategy Name' renombrada a 'Strategy_Name' para compatibilidad.")

    print("[TEST] Inicializando DataManager y cargando datos...")
    dm = DataManager()
    dm._kpis_data = df_kpi

    config = {
        'data_manager': dm,
        'kpis_selected': ["CAGR", "Drawdown", "Profit factor"],
        'trading_style': 'Intradía',
        'alpha': 0.05,
        'top_n': 10,
        'percentil': 0.95,
        'is_oos_split': 0.70,
        'filtrado_estricto': True,
        'analysis_type': 'unified'
    }

    print("[TEST] Ejecutando análisis robusto...")
    results, summary = run_complete_analysis_with_gui_integration(
        df_kpi,
        config=config,
        progress_callback=None
    )
    print("[TEST] Análisis completado.")

    if results is None or results.empty:
        print("[TEST][ERROR] El análisis no produjo resultados válidos.")
        sys.exit(2)

    print("[TEST] === RESUMEN DEL ANÁLISIS ===")
    print(summary)
    print(f"[TEST] Estrategias analizadas: {len(results)}")
    print("[TEST] Primeras 10 filas del resultado:")
    print(results.head(10))

    results.to_csv(output_path, index=False)
    print(f"[TEST] Resultados exportados a {output_path}")
    print("[TEST] Flujo de análisis terminal finalizado con éxito.")

except Exception as e:
    print("[TEST][EXCEPCIÓN DETECTADA]")
    print(str(e))
    print(traceback.format_exc())
    sys.exit(99) 