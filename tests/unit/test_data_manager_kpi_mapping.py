#!/usr/bin/env python3
"""
Test profesional de mapeo y limpieza de columnas estándar con DataManager
"""
import sys
import os
import logging

# Añadir src/ al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.data_manager import DataManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_data_manager_kpi_mapping.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

def main():
    log.info("=== TEST PROFESIONAL DATAMANAGER: MAPEADO Y LIMPIEZA DE KPIS ===")
    dm = DataManager()
    df = dm.load_and_prepare_data_pipeline("INPUTTEST/DatabankExport_M1.csv")
    if df is None or df.empty:
        log.error("❌ DataFrame vacío tras carga con DataManager")
        sys.exit(1)
    columnas_estandar = [
        'strategy_name', 'cagr_is', 'cagr_oos', 'sharpe_ratio_is', 'sharpe_ratio_oos',
        'profit_factor_is', 'profit_factor_oos', 'max_dd_pct', 'calmarratio_is', 'calmarratio_oos',
        'number_of_trades', 'winning_percent_is', 'winning_percent_oos'
    ]
    # Validar presencia y unicidad
    faltantes = [col for col in columnas_estandar if col not in df.columns]
    duplicados = df.columns[df.columns.duplicated()].tolist()
    if faltantes:
        log.error(f"❌ Columnas estándar faltantes: {faltantes}")
    else:
        log.info("✅ Todas las columnas estándar presentes")
    if duplicados:
        log.error(f"❌ Columnas estándar duplicadas: {duplicados}")
    else:
        log.info("✅ Sin columnas estándar duplicadas")
    # Mostrar ejemplos de los primeros valores
    for col in columnas_estandar:
        if col in df.columns:
            ejemplo = df[col].iloc[0] if not df[col].empty else 'VACIO'
            log.info(f"Columna '{col}': ejemplo -> {ejemplo}")
    log.info("=== TEST FINALIZADO ===")

if __name__ == "__main__":
    main() 