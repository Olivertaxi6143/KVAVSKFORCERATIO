import sys
import os
import pandas as pd
import shutil
from src.data_manager import DataManager
from src.core_engine_enhanced import run_complete_analysis_with_gui_integration
import traceback

# Configuración de paths
kpi_path = "INPUTTEST/DatabankExport_M1.csv"
sqx_folder = "INPUTTEST/M1_NDX_UP_MQL4_136_STOP"
dest_folder = "output/sqx_top"

# Crear carpeta de destino si no existe
os.makedirs(dest_folder, exist_ok=True)

try:
    print('[CLI] Cargando archivo KPI con delimitador ";" y quotechar " ...')
    df_kpi = pd.read_csv(kpi_path, sep=';', quotechar='"', engine='python')
    print(f"[CLI] Columnas leídas: {list(df_kpi.columns)}")
    columnas_requeridas = ['Strategy Name', 'CAGR', 'Drawdown', 'Profit factor']
    faltantes = [col for col in columnas_requeridas if col not in df_kpi.columns]
    if faltantes:
        print(f"[CLI][ERROR] Faltan columnas requeridas en el archivo KPI: {faltantes}")
        sys.exit(1)
    print(f"[CLI] Archivo KPI cargado correctamente: {df_kpi.shape}")

    print("[CLI] Inicializando DataManager y cargando datos...")
    dm = DataManager()
    dm._kpis_data = df_kpi  # Cargar DataFrame directamente

    config = {
        "trading_style": "Intradía",
        "alpha": 0.8,
        "top_n": 20,
        "percentil": 80,
        "scientific_improvements": True,
        "selected_kpis": {col: {"enabled": True, "weight": 1.0} for col in df_kpi.columns},
        "data_manager": dm
    }

    print("[CLI] Ejecutando análisis robusto y científico...")
    results, summary = run_complete_analysis_with_gui_integration(
        kpi_path,
        config=config,
        progress_callback=None,
        analysis_type="unified"
    )
    print("[CLI] Análisis completado.")

    if results is None or results.empty:
        print("[CLI][ERROR] El análisis no produjo resultados válidos.")
        sys.exit(2)

    print("[CLI] === RESUMEN DEL ANÁLISIS ===")
    print(summary)
    print(f"[CLI] Estrategias analizadas: {len(results)}")

    # Filtrar estrategias que pasan el test científico (ejemplo: Unified_Score_Normalized >= 0.7)
    if 'Unified_Score_Normalized' in results.columns:
        seleccionadas = results[results['Unified_Score_Normalized'] >= 0.7]
    else:
        seleccionadas = results.head(20)  # fallback: top 20
    print(f"[CLI] Estrategias seleccionadas para exportar: {len(seleccionadas)}")

    # Guardar resultados completos
    results.to_csv("output/cli_analysis_results.csv", index=False)
    print("[CLI] Resultados exportados a output/cli_analysis_results.csv")

    # Copiar archivos .sqx de las seleccionadas
    nombres = seleccionadas['Strategy Name'] if 'Strategy Name' in seleccionadas.columns else seleccionadas.iloc[:,0]
    copiados = 0
    for nombre in nombres:
        posibles = [f for f in os.listdir(sqx_folder) if nombre in f and f.endswith('.sqx')]
        if posibles:
            print(f"[CLI] Copiando archivos .sqx para estrategia: {nombre} -> {posibles}")
        for sqx in posibles:
            shutil.copy2(os.path.join(sqx_folder, sqx), os.path.join(dest_folder, sqx))
            copiados += 1
    print(f"[CLI] Archivos .sqx copiados a {dest_folder}: {copiados}")
    print("[CLI] Flujo de análisis y exportación completado con éxito.")

except Exception as e:
    print("[CLI][EXCEPCIÓN DETECTADA]")
    print(str(e))
    print(traceback.format_exc())
    sys.exit(99) 