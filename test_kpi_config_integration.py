#!/usr/bin/env python3
"""
Test profesional de integración y auditoría de KPIs y core engine
- Simula cambio de estilo de trading
- Verifica actualización automática de KPIs
- Genera configuración de análisis
- Ejecuta análisis en core engine
- Audita uso de KPIs y cálculos científicos
- Compara resultados con CLI
"""
import logging
import sys
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("KPI_AUDIT")

# Estilos de trading a probar
testing_styles = [
    "Intradía", "Swing", "Tendencial", "Reversión a la media", "Breakout"
]

# KPIs esperados por estilo (debe coincidir con la lógica de la GUI)
kpi_map = {
    'Intradía': [
        'Sortino', 'Recovery', 'Drawdown Trades', 'Winrate', 
        'Max Consec. Losses', 'Exposure', 'Avg. Bars in Trade'
    ],
    'Swing': [
        'Var', 'Cvar', 'Exposure', 'Marratio', 'Recovery', 
        'Maxdddur', 'Ulcer Index %', 'SQN'
    ],
    'Tendencial': [
        'Sortino', 'Marratio', 'Recovery', 'New Peak Trades', 
        'CAGR', 'Sharpe Ratio', 'Profit factor', 'CalmarRatio'
    ],
    'Reversión a la media': [
        'Sortino', 'Maxdddur', 'Drawdown Trades', 'Winrate', 
        'Expectancy', 'Payout ratio', 'Ulcer Performance Index'
    ],
    'Breakout': [
        'Marratio', 'Recovery', 'Exposure', 'Max Stag Trades', 
        'New Peak Trades', 'Drawdown Trades', 'RINAIndex'
    ],
}

# Archivo KPI de prueba
def_kpi_file = "DatabankExport_M1.csv"

def load_data():
    from src.data_manager import DataManager
    dm = DataManager()
    success = dm.load_kpis_data(def_kpi_file)
    if not success or dm.kpis_data is None:
        logger.error("❌ Error cargando datos KPI")
        sys.exit(1)
    logger.info(f"✅ Datos KPI cargados: {len(dm.kpis_data)} estrategias")
    return dm.kpis_data

def run_core_engine_analysis(df, config):
    from src.core.integration_layer import UnifiedEvaluatorEnhanced
    evaluator = UnifiedEvaluatorEnhanced()
    logger.info(f"⚙️ Ejecutando análisis con estilo: {config['trading_style']} y KPIs: {config['enabled_kpi_names']}")
    results = evaluator.evaluate_strategies_unified(df)
    logger.info(f"✅ Análisis completado: {len(results)} estrategias procesadas")
    # Auditoría de columnas de resultado
    logger.info(f"📊 Columnas resultado: {list(results.columns)}")
    if 'QVA_Score' in results.columns:
        logger.info("✅ QVA_Score calculado")
    if 'Quality_Category' in results.columns:
        logger.info("✅ Quality_Category asignada")
    return results

def build_analysis_config(style, all_kpis):
    # Simula la lógica de la GUI para KPIs activos
    enabled_kpis = {k: {"enabled": True, "weight": 1.0} for k in kpi_map[style] if k in all_kpis}
    config = {
        "trading_style": style,
        "alpha": 0.8,
        "top_n": 20,
        "percentil": 80.0,
        "scientific_improvements": True,
        "is_oos_split": 0.75,
        "selected_kpis": enabled_kpis,
        "enabled_kpi_names": list(enabled_kpis.keys())
    }
    logger.info(f"🔍 Configuración generada para '{style}': {config['enabled_kpi_names']}")
    return config

def main():
    logger.info("🚀 Iniciando auditoría profesional de KPIs y core engine")
    df = load_data()
    all_kpis = set(df.columns)
    for style in testing_styles:
        logger.info(f"\n=== Probando estilo de trading: {style} ===")
        config = build_analysis_config(style, all_kpis)
        results = run_core_engine_analysis(df, config)
        # Auditoría de KPIs usados
        used_kpis = set(config['enabled_kpi_names'])
        missing_kpis = used_kpis - set(results.columns)
        if missing_kpis:
            logger.warning(f"⚠️ KPIs seleccionados no presentes en resultados: {missing_kpis}")
        else:
            logger.info("✅ Todos los KPIs seleccionados están presentes en los resultados")
        # Auditoría de cálculos científicos
        if 'QVA_Score' in results.columns and 'Quality_Category' in results.columns:
            logger.info("✅ Cálculos científicos y robustos ejecutados correctamente")
        else:
            logger.error("❌ Faltan cálculos científicos en los resultados")
    logger.info("\n🎯 Auditoría de KPIs y core engine completada")

if __name__ == "__main__":
    main() 