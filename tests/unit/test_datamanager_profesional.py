#!/usr/bin/env python3
"""
Ejemplo profesional de uso del DataManager para análisis y logs
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Añadir src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from data.data_manager import DataManager

def main():
    print("=== EJEMPLO PROFESIONAL DATAMANAGER ===")
    dm = DataManager()

    # 1. Cargar y limpiar datos
    df_clean = dm.get_clean_data("INPUTTEST/DatabankExport_M1.csv")
    print(f"✅ DataFrame limpio: {df_clean.shape}")
    print(df_clean.head(2))

    # 2. Análisis simple: describe KPIs
    analysis = df_clean.describe(include='all')
    print("\n=== Análisis simple (describe) ===")
    print(analysis)

    # 3. Guardar resultado de análisis
    analysis_name = f"describe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dm.save_analysis_result(analysis_name, analysis)
    print(f"✅ Resultado de análisis guardado como: {analysis_name}")

    # 4. Listar y cargar resultados de análisis
    print("\n=== Resultados de análisis disponibles ===")
    print(dm.list_analysis_results())
    loaded_analysis = dm.load_analysis_result(analysis_name)
    print(f"\n✅ Análisis cargado: {loaded_analysis.shape}")

    # 5. Guardar y consultar log de test
    log_text = "Test profesional ejecutado correctamente.\nSin errores."
    test_name = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dm.save_test_result(test_name, log_text)
    print(f"✅ Log de test guardado como: {test_name}")
    print("\n=== Logs de test disponibles ===")
    print(dm.list_test_results())
    loaded_log = dm.load_test_result(test_name)
    print(f"\n✅ Log de test cargado:\n{loaded_log}")

    print("\n✅ EJEMPLO PROFESIONAL COMPLETADO")

if __name__ == "__main__":
    main() 