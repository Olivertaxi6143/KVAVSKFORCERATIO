#!/usr/bin/env python3
"""
TEST_DIAGNOSTICO_GUI.py - Diagnóstico específico del problema del botón "Iniciar Análisis"

Este script simula exactamente lo que hace la GUI cuando presionas el botón "Iniciar Análisis"
para identificar dónde está fallando el proceso.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import time
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np

try:
    from src.data.data_manager import DataManager
    from src.core.integration_layer import (
        FactorKElite96Enhanced, 
        UnifiedEvaluatorEnhanced,
        run_complete_analysis_with_gui_integration,
        ProgressCallback
    )
    from src.gui.utils import load_data_with_datamanager as read_and_prepare
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_diagnostico_gui.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiagnosticoGUI:
    """
    Clase para diagnosticar el problema del botón "Iniciar Análisis" en la GUI.
    """
    
    def __init__(self):
        self.results = {}
        
    def simular_configuracion_gui(self) -> Dict[str, Any]:
        """
        Simula la configuración que tendría la GUI.
        
        Returns:
            Configuración simulada de la GUI
        """
        return {
            "kpi_file": "DatabankExport_M1.csv",
            "market_file": "DATOSMQL5.csv",
            "strategies_folder": "INPUTTEST/M1_NDX_UP_MQL4_136_STOP",
            "output_folder": "INPUTTEST/TOP",
            "trading_style": "Intradía",
            "alpha": 0.8,
            "percentil": 95,
            "is_oos_split": 75,  # 75%
            "scientific_improvements": True,
            "selected_metrics": [
                "CAGR", "Profit factor", "Sharpe Ratio", "Winning Percent", "Net profit",
                "Drawdown", "CalmarRatio", "Max Consec. Losses", "Ulcer Index %", "VaR (95%)",
                "SQN", "RINAIndex", "RecoveryFactor", "Sortino Ratio", "CVaR (95%)",
                "Exposure", "Avg. Bars in Trade", "Max Drawdown Duration", "Payout ratio"
            ]
        }
    
    def simular_validaciones_gui(self, config: Dict[str, Any]) -> bool:
        """
        Simula las validaciones que hace la GUI antes de iniciar el análisis.
        
        Args:
            config: Configuración simulada
            
        Returns:
            True si las validaciones pasan
        """
        logger.info("🔍 Simulando validaciones de la GUI...")
        
        # Validación 1: Archivo KPI existe
        if not os.path.exists(config["kpi_file"]):
            logger.error(f"❌ Archivo KPI no encontrado: {config['kpi_file']}")
            return False
        logger.info(f"✅ Archivo KPI encontrado: {config['kpi_file']}")
        
        # Validación 2: Archivo de mercado existe
        if not os.path.exists(config["market_file"]):
            logger.warning(f"⚠️ Archivo de mercado no encontrado: {config['market_file']}")
            # La GUI usa un archivo por defecto
            default_market = "DATOSMQL5.csv"
            if os.path.exists(default_market):
                config["market_file"] = default_market
                logger.info(f"✅ Usando archivo de mercado por defecto: {default_market}")
            else:
                logger.warning("⚠️ No se encontró archivo de mercado por defecto")
        
        # Validación 3: Carpeta de estrategias existe
        if not os.path.exists(config["strategies_folder"]):
            logger.warning(f"⚠️ Carpeta de estrategias no encontrada: {config['strategies_folder']}")
        
        # Validación 4: Carpeta de salida existe o se puede crear
        output_path = Path(config["output_folder"])
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Carpeta de salida creada: {config['output_folder']}")
            except Exception as e:
                logger.error(f"❌ No se pudo crear carpeta de salida: {e}")
                return False
        
        logger.info("✅ Todas las validaciones pasaron")
        return True
    
    def simular_carga_datos_gui(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula la carga de datos que hace la GUI usando read_and_prepare.
        
        Args:
            config: Configuración simulada
            
        Returns:
            Resultados de la carga de datos
        """
        logger.info("📊 Simulando carga de datos de la GUI...")
        
        try:
            # Simular la carga usando read_and_prepare como lo hace la GUI
            is_split = config["is_oos_split"] / 100.0
            df_kpi_clean = read_and_prepare(config["kpi_file"], is_oos_split=is_split)
            
            if df_kpi_clean is None or df_kpi_clean.empty:
                raise ValueError("No se pudieron cargar los datos del KPI")
            
            logger.info(f"✅ Datos cargados: {len(df_kpi_clean)} estrategias")
            logger.info(f"📋 Columnas disponibles: {list(df_kpi_clean.columns)}")
            
            # Validar columnas requeridas como lo hace la GUI
            required_cols = {'CAGR', 'Drawdown', 'Expectancy', 'Max Consec. Losses', 
                           'Sharpe Ratio', 'Profit factor', 'RINAIndex', 'Ulcer Index %', 
                           '# of trades', 'CalmarRatio'}
            missing_cols = required_cols - set(df_kpi_clean.columns)
            
            if missing_cols:
                logger.warning(f"⚠️ Columnas requeridas faltantes: {missing_cols}")
                
                # Simular el cálculo automático de CalmarRatio como lo hace la GUI
                if 'CalmarRatio' in missing_cols and 'RecoveryFactor' in df_kpi_clean.columns and 'Drawdown' in df_kpi_clean.columns:
                    try:
                        df_kpi_clean['RecoveryFactor'] = pd.to_numeric(df_kpi_clean['RecoveryFactor'], errors='coerce')
                        df_kpi_clean['Drawdown'] = pd.to_numeric(df_kpi_clean['Drawdown'], errors='coerce').abs()
                        df_kpi_clean['CalmarRatio'] = df_kpi_clean['RecoveryFactor'] / df_kpi_clean['Drawdown'].replace(0, np.nan).fillna(1e-6)
                        logger.info("✅ Calculada columna 'CalmarRatio' automáticamente")
                    except Exception as e:
                        logger.error(f"❌ Error calculando CalmarRatio: {str(e)}")
                        df_kpi_clean['CalmarRatio'] = np.random.uniform(1.5, 4.0, len(df_kpi_clean))
                        logger.warning("⚠️ Usando valores placeholder para 'CalmarRatio'")
            
            return {
                "success": True,
                "data": df_kpi_clean,
                "total_estrategias": len(df_kpi_clean)
            }
            
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def simular_preparacion_configuracion_gui(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula la preparación de configuración que hace la GUI.
        
        Args:
            config: Configuración simulada
            
        Returns:
            Configuración preparada para el motor de análisis
        """
        logger.info("⚙️ Simulando preparación de configuración de la GUI...")
        
        # Mapeo de estilos de GUI a estilos del motor (como lo hace la GUI)
        style_mapping = {
            'Intradía': 'Intraday',
            'Swing': 'Swing',
            'Tendencial': 'Trend Following',
            'Reversión a la media': 'Mean Reversion',
            'Breakout': 'Breakout'
        }
        
        engine_style = style_mapping.get(config["trading_style"], 'General')
        
        # Configuración de KPIs extra según el estilo (como lo hace la GUI)
        extra_kpis_config = {
            'Intraday': {
                'Winrate': {'weight': 0.25, 'description': 'Frecuencia de éxito en trading de alta frecuencia'},
                'Avgtradedur': {'weight': 0.15, 'description': 'Duración promedio de operaciones'},
                'Exposure': {'weight': 0.20, 'description': 'Tiempo en el mercado'},
                'SQN': {'weight': 0.20, 'description': 'Calidad del sistema de trading'},
                'Sortino': {'weight': 0.20, 'description': 'Ratio de Sortino para riesgo asimétrico'}
            }
        }
        
        # Preparar configuración como lo hace la GUI
        analysis_config = {
            "trading_style": engine_style,
            "gui_trading_style": config["trading_style"],
            "alpha": config["alpha"],
            "top_n": 20,  # Valor por defecto
            "percentil": config["percentil"],
            "is_oos_split": config["is_oos_split"] / 100.0,
            "scientific_improvements": config["scientific_improvements"],
            "selected_metrics": config["selected_metrics"],
            "extra_kpis_config": extra_kpis_config.get(engine_style, {})
        }
        
        logger.info(f"✅ Configuración preparada: {analysis_config}")
        return analysis_config
    
    def simular_analisis_gui(self, config: Dict[str, Any], analysis_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula el análisis que hace la GUI usando run_complete_analysis_with_gui_integration.
        
        Args:
            config: Configuración simulada
            analysis_config: Configuración de análisis
            
        Returns:
            Resultados del análisis
        """
        logger.info("🚀 Simulando análisis de la GUI...")
        
        try:
            # Crear ProgressCallback como lo hace la GUI
            progress_callback = ProgressCallback()
            
            # Ejecutar análisis como lo hace la GUI
            results, summary = run_complete_analysis_with_gui_integration(
                config["kpi_file"],
                config=analysis_config,
                progress_callback=progress_callback,
                analysis_type="unified"
            )
            
            if results is None or results.empty:
                raise ValueError("El análisis no produjo resultados válidos")
            
            logger.info(f"✅ Análisis completado: {len(results)} estrategias procesadas")
            
            # Verificar columnas de score como lo hace la GUI
            score_cols = [col for col in results.columns if 'QVA' in col or 'Unified_Score' in col or 'Score' in col]
            if not score_cols:
                logger.warning("⚠️ No se encontraron columnas de score en los resultados")
            else:
                logger.info(f"📊 Columnas de score encontradas: {score_cols}")
                for col in score_cols:
                    if col in results.columns and pd.api.types.is_numeric_dtype(results[col]):
                        stats = results[col].describe()
                        logger.info(f"📈 {col}: min={stats['min']:.4f}, max={stats['max']:.4f}, mean={stats['mean']:.4f}")
            
            return {
                "success": True,
                "results": results,
                "summary": summary,
                "total_estrategias": len(results)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "results": None,
                "summary": None
            }
    
    def ejecutar_diagnostico_completo(self) -> Dict[str, Any]:
        """
        Ejecuta el diagnóstico completo del problema del botón "Iniciar Análisis".
        
        Returns:
            Resultados del diagnóstico
        """
        logger.info("🔬 INICIANDO DIAGNÓSTICO COMPLETO DEL BOTÓN 'INICIAR ANÁLISIS'")
        logger.info("=" * 80)
        
        start_time = time.time()
        results = {
            "start_time": time.time(),
            "steps": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Paso 1: Simular configuración de la GUI
            logger.info("📋 Paso 1: Simulando configuración de la GUI...")
            config = self.simular_configuracion_gui()
            results["steps"]["config"] = {"success": True, "config": config}
            
            # Paso 2: Simular validaciones de la GUI
            logger.info("🔍 Paso 2: Simulando validaciones de la GUI...")
            validations_result = self.simular_validaciones_gui(config)
            results["steps"]["validations"] = {"success": validations_result}
            
            if not validations_result:
                results["errors"].append("Las validaciones de la GUI fallaron")
                return results
            
            # Paso 3: Simular carga de datos de la GUI
            logger.info("📊 Paso 3: Simulando carga de datos de la GUI...")
            data_result = self.simular_carga_datos_gui(config)
            results["steps"]["data_loading"] = data_result
            
            if not data_result["success"]:
                results["errors"].append(f"Error cargando datos: {data_result['error']}")
                return results
            
            # Paso 4: Simular preparación de configuración de la GUI
            logger.info("⚙️ Paso 4: Simulando preparación de configuración de la GUI...")
            analysis_config = self.simular_preparacion_configuracion_gui(config)
            results["steps"]["config_preparation"] = {"success": True, "config": analysis_config}
            
            # Paso 5: Simular análisis de la GUI
            logger.info("🚀 Paso 5: Simulando análisis de la GUI...")
            analysis_result = self.simular_analisis_gui(config, analysis_config)
            results["steps"]["analysis"] = analysis_result
            
            if not analysis_result["success"]:
                results["errors"].append(f"Error en análisis: {analysis_result['error']}")
                return results
            
            # Calcular tiempo total
            execution_time = time.time() - start_time
            results["execution_time"] = execution_time
            results["success"] = True
            
            logger.info(f"✅ DIAGNÓSTICO COMPLETADO EN {execution_time:.2f} segundos")
            logger.info("=" * 80)
            
        except Exception as e:
            results["errors"].append(f"Error general: {str(e)}")
            results["success"] = False
            logger.error(f"❌ Error en diagnóstico: {e}")
        
        return results

def main():
    """Función principal para ejecutar el diagnóstico."""
    print("DIAGNÓSTICO DEL BOTÓN 'INICIAR ANÁLISIS'")
    print("=" * 60)
    print("Este script simula exactamente lo que hace la GUI cuando presionas")
    print("el botón 'Iniciar Análisis' para identificar dónde está fallando.")
    print()
    
    diagnostico = DiagnosticoGUI()
    results = diagnostico.ejecutar_diagnostico_completo()
    
    # Mostrar resumen
    print("\n" + "=" * 80)
    print("RESUMEN DEL DIAGNÓSTICO")
    print("=" * 80)
    
    if results["success"]:
        print("✅ DIAGNÓSTICO EXITOSO")
        print(f"⏱️ Tiempo total: {results['execution_time']:.2f} segundos")
        
        # Mostrar detalles de cada paso
        for step_name, step_result in results["steps"].items():
            if step_result.get("success", False):
                print(f"✅ {step_name}: EXITOSO")
            else:
                print(f"❌ {step_name}: FALLIDO")
                if "error" in step_result:
                    print(f"   Error: {step_result['error']}")
    else:
        print("❌ DIAGNÓSTICO FALLIDO")
        for error in results["errors"]:
            print(f"❌ Error: {error}")
    
    print("\n🎯 Si el diagnóstico es exitoso, el problema está en la GUI.")
    print("🎯 Si el diagnóstico falla, el problema está en el backend.")

if __name__ == "__main__":
    main() 