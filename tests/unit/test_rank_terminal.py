import sys
import os
import pandas as pd
import traceback
import pytest
from src.data.data_manager import DataManager
from src.core.integration_layer import run_complete_analysis_with_gui_integration

def test_rank_terminal():
    """Test del flujo completo de análisis terminal."""
    # Rutas de entrada/salida en INPUTTEST
    kpi_path = "INPUTTEST/DatabankExport_M1.csv"
    output_path = "INPUTTEST/cli_analysis_results.csv"

    try:
        print('[TEST] Cargando archivo KPI...')
        df_kpi = pd.read_csv(kpi_path, sep=',', quotechar='"', engine='python')
        print(f"[TEST] Columnas leídas: {list(df_kpi.columns)}")
        
        # Verificar que las columnas requeridas estén presentes
        columnas_requeridas = ['Strategy_Name', 'CAGR', 'Max_Drawdown', 'Profit_factor']
        faltantes = [col for col in columnas_requeridas if col not in df_kpi.columns]
        if faltantes:
            print(f"[TEST][ERROR] Faltan columnas requeridas en el archivo KPI: {faltantes}")
            print(f"[TEST] Columnas disponibles: {list(df_kpi.columns)}")
            pytest.fail(f"Faltan columnas requeridas: {faltantes}")
        
        print(f"[TEST] Archivo KPI cargado correctamente: {df_kpi.shape}")

        print("[TEST] Inicializando DataManager y cargando datos...")
        dm = DataManager()
        dm._kpis_data = df_kpi

        config = {
            'data_manager': dm,
            'kpis_selected': ["CAGR", "Max_Drawdown", "Profit_factor"],
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
            pytest.fail("El análisis no produjo resultados válidos")

        print("[TEST] === RESUMEN DEL ANÁLISIS ===")
        print(summary)
        print(f"[TEST] Estrategias analizadas: {len(results)}")
        print("[TEST] Primeras 10 filas del resultado:")
        print(results.head(10))

        results.to_csv(output_path, index=False)
        print(f"[TEST] Resultados exportados a {output_path}")
        print("[TEST] Flujo de análisis terminal finalizado con éxito.")
        
        # Assertions para validar el test
        assert results is not None, "Los resultados no deben ser None"
        assert not results.empty, "Los resultados no deben estar vacíos"
        assert len(results) > 0, "Debe haber al menos una estrategia en los resultados"
        assert 'Strategy_Name' in results.columns, "Los resultados deben tener la columna Strategy_Name"

    except Exception as e:
        print("[TEST][EXCEPCIÓN DETECTADA]")
        print(str(e))
        print(traceback.format_exc())
        pytest.fail(f"Excepción durante el test: {str(e)}") 