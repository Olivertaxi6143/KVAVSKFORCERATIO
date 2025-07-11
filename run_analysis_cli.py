import sys
import pandas as pd
from src.data_manager import DataManager
from src.core_engine_enhanced import run_complete_analysis_with_gui_integration
import traceback

# Rutas de ejemplo (ajusta si es necesario)
kpi_path = "INPUTTEST/DatabankExport_M1.csv"

try:
    print("[INFO] Inicializando DataManager y cargando datos...")
    dm = DataManager()
    if not dm.load_kpis_data(kpi_path):
        print(f"[ERROR] No se pudo cargar el archivo KPI: {kpi_path}")
        sys.exit(1)
    df_kpi = dm.get_kpis_data()
    print(f"✅ Archivo KPI cargado: {df_kpi.shape}")

    # 2. Preparar configuración mínima
    config = {
        "trading_style": "Intradía",
        "alpha": 0.8,
        "top_n": 20,
        "percentil": 80,
        "scientific_improvements": True,
        "selected_kpis": {col: {"enabled": True, "weight": 1.0} for col in df_kpi.columns},
        "data_manager": dm
    }

    print("[INFO] Ejecutando análisis robusto...")
    results, summary = run_complete_analysis_with_gui_integration(
        kpi_path,
        config=config,
        progress_callback=None,
        analysis_type="unified"
    )

    if results is None or results.empty:
        print("[ERROR] El análisis no produjo resultados válidos.")
        sys.exit(2)

    # 4. Mostrar resumen en consola
    print("=== RESUMEN DEL ANÁLISIS ===")
    print(summary)
    print("=== TOP 5 ESTRATEGIAS ===")
    print(results.head())

    # 5. (Opcional) Exportar resultados
    results.to_csv("output/cli_analysis_results.csv", index=False)
    print("✅ Resultados exportados a output/cli_analysis_results.csv")

except Exception as e:
    print("[EXCEPCIÓN DETECTADA]")
    print(str(e))
    print(traceback.format_exc())
    sys.exit(99) 