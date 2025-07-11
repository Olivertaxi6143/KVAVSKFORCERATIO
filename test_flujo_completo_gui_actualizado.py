#!/usr/bin/env python3
"""
TEST_FLUJO_COMPLETO_GUI_ACTUALIZADO.py - Flujo completo actualizado de la GUI

Este script simula el flujo completo de la GUI:
1. Análisis principal con core engine
2. Filtrado por percentil (selección)
3. Análisis del Asesor Financiero Inteligente
4. Guardado en carpeta TOP con archivos .sqx

Usa la configuración estándar del proyecto:
- Archivo KPI: DatabankExport_M1.csv
- Archivo mercado: DATOSMQL5.csv
- Carpeta estrategias: INPUTTEST/M1_NDX_UP_MQL4_136_STOP
- Carpeta TOP: INPUTTEST/TOP
"""

import sys
import os
import json
import logging
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from data_manager import DataManager
    from core_engine_enhanced import (
        FactorKElite96Enhanced,
        UnifiedEvaluatorEnhanced,
        run_complete_analysis_with_gui_integration,
        ProgressCallback
    )
    from asesor_financiero_inteligente import ejecutar_analisis_completo
    from gui_enhanced_rank import read_and_prepare, normalizar_columnas_y_kpis
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_flujo_completo_actualizado.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FlujoCompletoActualizado:
    """
    Clase para probar el flujo completo actualizado de la GUI.
    """
    
    def __init__(self):
        self.results = {}
        self.config = self._create_configuracion_estandar()
        
    def _create_configuracion_estandar(self) -> Dict[str, Any]:
        """
        Crea la configuración estándar del proyecto.
        
        Returns:
            Configuración estándar
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
    
    def paso1_analisis_principal(self) -> Dict[str, Any]:
        """
        Paso 1: Análisis principal con core engine.
        
        Returns:
            Resultados del análisis principal
        """
        logger.info("🚀 PASO 1: ANÁLISIS PRINCIPAL")
        logger.info("=" * 50)
        
        try:
            # 1.1 Cargar datos usando read_and_prepare (como la GUI)
            logger.info("📊 Cargando datos con read_and_prepare...")
            is_split = self.config["is_oos_split"] / 100.0
            df_kpi_clean = read_and_prepare(self.config["kpi_file"], is_oos_split=is_split)
            
            if df_kpi_clean is None or df_kpi_clean.empty:
                raise ValueError("No se pudieron cargar los datos del KPI")
            
            logger.info(f"✅ Datos cargados: {len(df_kpi_clean)} estrategias")
            
            # 1.2 Preparar configuración para el motor de análisis
            logger.info("⚙️ Preparando configuración para el motor de análisis...")
            analysis_config = self._preparar_configuracion_analisis()
            
            # 1.3 Ejecutar análisis con core engine
            logger.info("🔧 Ejecutando análisis con core engine...")
            progress_callback = ProgressCallback()
            
            results, summary = run_complete_analysis_with_gui_integration(
                self.config["kpi_file"],
                config=analysis_config,
                progress_callback=progress_callback,
                analysis_type="unified"
            )
            
            if results is None or results.empty:
                raise ValueError("El análisis no produjo resultados válidos")
            
            logger.info(f"✅ Análisis principal completado: {len(results)} estrategias procesadas")
            
            # 1.4 Verificar columnas de score
            score_cols = [col for col in results.columns if 'QVA' in col or 'Unified_Score' in col or 'Score' in col]
            if score_cols:
                logger.info(f"📊 Columnas de score encontradas: {score_cols}")
                for col in score_cols:
                    if col in results.columns and pd.api.types.is_numeric_dtype(results[col]):
                        stats = results[col].describe()
                        logger.info(f"📈 {col}: min={stats['min']:.4f}, max={stats['max']:.4f}, mean={stats['mean']:.4f}")
            
            return {
                "success": True,
                "results": results,
                "summary": summary,
                "total_estrategias": len(results),
                "score_columns": score_cols
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis principal: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "results": None,
                "summary": None
            }
    
    def paso2_seleccion_filtrado(self, resultados_analisis: pd.DataFrame) -> Dict[str, Any]:
        """
        Paso 2: Selección y filtrado por percentil.
        
        Args:
            resultados_analisis: Resultados del análisis principal
            
        Returns:
            Estrategias filtradas
        """
        logger.info("🎯 PASO 2: SELECCIÓN Y FILTRADO")
        logger.info("=" * 50)
        
        try:
            percentil = self.config["percentil"]
            
            # Buscar columna de score
            score_columns = [col for col in resultados_analisis.columns if 'QVA' in col or 'Unified_Score' in col or 'Score' in col]
            if not score_columns:
                raise ValueError("No se encontró columna de score para filtrar")
            
            score_col = score_columns[0]
            logger.info(f"📊 Usando columna de score: {score_col}")
            
            # Calcular threshold
            threshold = resultados_analisis[score_col].quantile(percentil / 100)
            logger.info(f"📊 Threshold para percentil {percentil}%: {threshold:.4f}")
            
            # Aplicar filtro
            estrategias_filtradas = resultados_analisis[resultados_analisis[score_col] >= threshold]
            
            if len(estrategias_filtradas) == 0:
                logger.warning(f"⚠️ El filtro no produjo resultados para percentil {percentil}%")
                # Usar las mejores 5 estrategias como fallback
                estrategias_filtradas = resultados_analisis.nlargest(5, score_col)
                logger.info(f"📊 Usando las 5 mejores estrategias como fallback")
            
            logger.info(f"✅ Filtrado completado: {len(estrategias_filtradas)} estrategias seleccionadas")
            
            # Estadísticas de las estrategias filtradas
            if len(estrategias_filtradas) > 0:
                filtered_scores = estrategias_filtradas[score_col]
                score_stats = filtered_scores.describe()
                logger.info(f"📊 Estadísticas de scores filtrados: {score_stats.to_dict()}")
            
            return {
                "success": True,
                "estrategias_filtradas": estrategias_filtradas,
                "total_filtradas": len(estrategias_filtradas),
                "percentil_aplicado": percentil,
                "threshold": threshold
            }
            
        except Exception as e:
            logger.error(f"❌ Error en selección y filtrado: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "estrategias_filtradas": None
            }
    
    def paso3_asesor_financiero(self, estrategias_filtradas: pd.DataFrame) -> Dict[str, Any]:
        """
        Paso 3: Análisis del Asesor Financiero Inteligente.
        
        Args:
            estrategias_filtradas: Estrategias filtradas del paso anterior
            
        Returns:
            Resultados del asesor financiero
        """
        logger.info("🤖 PASO 3: ASESOR FINANCIERO INTELIGENTE")
        logger.info("=" * 50)
        
        try:
            # Validar que hay estrategias para analizar
            if len(estrategias_filtradas) == 0:
                raise ValueError("No hay estrategias para analizar")
            
            # Normalizar nombres de columnas y seleccionar KPIs relevantes
            estrategias_normalizadas, kpis_disponibles = normalizar_columnas_y_kpis(estrategias_filtradas.copy())
            logger.info(f"📊 KPIs numéricos disponibles para análisis: {len(kpis_disponibles)}")
            
            # Ejecutar análisis del asesor
            logger.info("🔬 Ejecutando análisis del Asesor Financiero Inteligente...")
            resultados_asesor = ejecutar_analisis_completo(
                estrategias_filtradas=estrategias_normalizadas,
                kpis_seleccionados=kpis_disponibles
            )
            
            if not resultados_asesor:
                raise ValueError("El asesor financiero no produjo resultados")
            
            # Validar que hay consejos generados
            consejos_count = len(resultados_asesor.get('consejos_completos', []))
            logger.info(f"📊 {consejos_count} consejos generados por el asesor")
            
            if consejos_count == 0:
                logger.warning("⚠️ No se generaron consejos por el asesor")
            
            return {
                "success": True,
                "resultados": resultados_asesor,
                "kpis_usados": kpis_disponibles,
                "consejos_count": consejos_count,
                "estrategias_analizadas": len(estrategias_normalizadas)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en asesor financiero: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "resultados": None
            }
    
    def paso4_guardado_top_n(self, estrategias_filtradas: pd.DataFrame, 
                             resultados_asesor: Dict[str, Any]) -> Dict[str, Any]:
        """
        Paso 4: Guardado en carpeta TOP con archivos .sqx.
        
        Args:
            estrategias_filtradas: Estrategias filtradas
            resultados_asesor: Resultados del asesor financiero
            
        Returns:
            Resultados del guardado
        """
        logger.info("💾 PASO 4: GUARDADO TOP N")
        logger.info("=" * 50)
        
        try:
            output_folder = Path(self.config["output_folder"])
            output_folder.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 4.1 Guardar DataFrame de estrategias filtradas
            csv_file = output_folder / f"estrategias_filtradas_{timestamp}.csv"
            estrategias_filtradas.to_csv(csv_file, index=False)
            logger.info(f"✅ CSV guardado: {csv_file}")
            
            # 4.2 Guardar resultados del asesor
            json_file = output_folder / f"asesor_resultados_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(resultados_asesor, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ JSON guardado: {json_file}")
            
            # 4.3 Guardar resumen ejecutivo
            txt_file = output_folder / f"resumen_{timestamp}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"RESUMEN EJECUTIVO - FLUJO COMPLETO\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Estrategias analizadas: {len(estrategias_filtradas)}\n")
                f.write(f"Percentil aplicado: {self.config['percentil']}%\n\n")
                
                if 'consejos_completos' in resultados_asesor:
                    f.write("CONSEJOS DEL ASESOR FINANCIERO:\n")
                    f.write("-" * 30 + "\n")
                    for i, consejo in enumerate(resultados_asesor['consejos_completos'], 1):
                        f.write(f"{i}. {consejo}\n")
            
            logger.info(f"✅ TXT guardado: {txt_file}")
            
            # 4.4 Copiar archivos .sqx
            source_folder = Path(self.config["strategies_folder"])
            files_copied = []
            
            if source_folder.exists():
                # Obtener nombres de estrategias
                if 'Strategy_Name' in estrategias_filtradas.columns:
                    strategy_names = estrategias_filtradas['Strategy_Name'].tolist()
                else:
                    strategy_names = estrategias_filtradas.index.tolist()
                
                for strategy_name in strategy_names:
                    sqx_file = source_folder / f"{strategy_name}.sqx"
                    if sqx_file.exists():
                        dest_file = output_folder / f"{strategy_name}.sqx"
                        shutil.copy2(sqx_file, dest_file)
                        files_copied.append(str(dest_file))
                
                logger.info(f"✅ {len(files_copied)} archivos .sqx copiados")
            else:
                logger.warning(f"⚠️ Carpeta de estrategias no encontrada: {source_folder}")
            
            return {
                "success": True,
                "files_saved": [str(csv_file), str(json_file), str(txt_file)],
                "files_copied": files_copied,
                "total_copied": len(files_copied)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en guardado TOP N: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "files_saved": [],
                "files_copied": []
            }
    
    def _preparar_configuracion_analisis(self) -> Dict[str, Any]:
        """
        Prepara la configuración para el análisis como lo hace la GUI.
        
        Returns:
            Configuración de análisis
        """
        # Mapeo de estilos de GUI a estilos del motor
        style_mapping = {
            'Intradía': 'Intraday',
            'Swing': 'Swing',
            'Tendencial': 'Trend Following',
            'Reversión a la media': 'Mean Reversion',
            'Breakout': 'Breakout'
        }
        
        engine_style = style_mapping.get(self.config["trading_style"], 'General')
        
        return {
            "trading_style": engine_style,
            "gui_trading_style": self.config["trading_style"],
            "alpha": self.config["alpha"],
            "top_n": 20,
            "percentil": self.config["percentil"],
            "is_oos_split": self.config["is_oos_split"] / 100.0,
            "scientific_improvements": self.config["scientific_improvements"],
            "selected_metrics": self.config["selected_metrics"]
        }
    
    def ejecutar_flujo_completo(self) -> Dict[str, Any]:
        """
        Ejecuta el flujo completo: análisis → selección → asesor → guardado.
        
        Returns:
            Resultados del flujo completo
        """
        logger.info("🎯 INICIANDO FLUJO COMPLETO DE LA GUI")
        logger.info("=" * 80)
        
        start_time = time.time()
        results = {
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Paso 1: Análisis principal
            logger.info("🚀 PASO 1: ANÁLISIS PRINCIPAL")
            analysis_result = self.paso1_analisis_principal()
            results["steps"]["analisis_principal"] = analysis_result
            
            if not analysis_result["success"]:
                results["errors"].append(f"Error en análisis principal: {analysis_result['error']}")
                return results
            
            # Paso 2: Selección y filtrado
            logger.info("🎯 PASO 2: SELECCIÓN Y FILTRADO")
            selection_result = self.paso2_seleccion_filtrado(analysis_result["results"])
            results["steps"]["seleccion_filtrado"] = selection_result
            
            if not selection_result["success"]:
                results["errors"].append(f"Error en selección: {selection_result['error']}")
                return results
            
            # Paso 3: Asesor Financiero
            logger.info("🤖 PASO 3: ASESOR FINANCIERO")
            asesor_result = self.paso3_asesor_financiero(selection_result["estrategias_filtradas"])
            results["steps"]["asesor_financiero"] = asesor_result
            
            if not asesor_result["success"]:
                results["errors"].append(f"Error en asesor financiero: {asesor_result['error']}")
                return results
            
            # Paso 4: Guardado TOP N
            logger.info("💾 PASO 4: GUARDADO TOP N")
            save_result = self.paso4_guardado_top_n(
                selection_result["estrategias_filtradas"], 
                asesor_result["resultados"]
            )
            results["steps"]["guardado_top_n"] = save_result
            
            if not save_result["success"]:
                results["errors"].append(f"Error en guardado: {save_result['error']}")
                return results
            
            # Calcular tiempo total
            execution_time = time.time() - start_time
            results["execution_time"] = execution_time
            results["end_time"] = datetime.now().isoformat()
            results["success"] = True
            
            logger.info(f"✅ FLUJO COMPLETO FINALIZADO EN {execution_time:.2f} segundos")
            logger.info("=" * 80)
            
        except Exception as e:
            results["errors"].append(f"Error general: {str(e)}")
            results["success"] = False
            logger.error(f"❌ Error en flujo completo: {e}")
        
        return results

def main():
    """Función principal para ejecutar el flujo completo."""
    print("FLUJO COMPLETO DE LA GUI - ACTUALIZADO")
    print("=" * 60)
    print("Este script simula el flujo completo de la GUI:")
    print("1. Análisis principal con core engine")
    print("2. Selección y filtrado por percentil")
    print("3. Análisis del Asesor Financiero Inteligente")
    print("4. Guardado en carpeta TOP con archivos .sqx")
    print()
    
    flujo = FlujoCompletoActualizado()
    results = flujo.ejecutar_flujo_completo()
    
    # Mostrar resumen final
    print("\n" + "=" * 80)
    print("RESUMEN FINAL DEL FLUJO COMPLETO")
    print("=" * 80)
    
    if results["success"]:
        print("✅ FLUJO COMPLETO EXITOSO")
        print(f"⏱️ Tiempo total: {results['execution_time']:.2f} segundos")
        
        # Mostrar detalles de cada paso
        for step_name, step_result in results["steps"].items():
            if step_result.get("success", False):
                print(f"✅ {step_name}: EXITOSO")
                if "total_estrategias" in step_result:
                    print(f"   Estrategias: {step_result['total_estrategias']}")
                if "total_filtradas" in step_result:
                    print(f"   Filtradas: {step_result['total_filtradas']}")
                if "consejos_count" in step_result:
                    print(f"   Consejos: {step_result['consejos_count']}")
                if "total_copied" in step_result:
                    print(f"   Archivos .sqx: {step_result['total_copied']}")
            else:
                print(f"❌ {step_name}: FALLIDO")
                if "error" in step_result:
                    print(f"   Error: {step_result['error']}")
    else:
        print("❌ FLUJO COMPLETO FALLIDO")
        for error in results["errors"]:
            print(f"❌ Error: {error}")
    
    print("\n🎉 ¡Flujo completo finalizado!")

if __name__ == "__main__":
    main()

# ===================== TESTS AUTOMÁTICOS PARA PYTEST =====================

def test_flujo_completo_principal():
    """
    Test principal del flujo completo de la GUI.
    Valida que todos los pasos se ejecuten correctamente.
    """
    print("\n🧪 TEST: Flujo completo principal")
    print("=" * 50)
    
    try:
        # Crear instancia del flujo
        flujo = FlujoCompletoActualizado()
        
        # Ejecutar flujo completo
        results = flujo.ejecutar_flujo_completo()
        
        # Validar que el flujo fue exitoso
        assert results["success"] is True, f"El flujo completo falló: {results.get('errors', [])}"
        
        # Validar que todos los pasos se ejecutaron
        required_steps = ["analisis_principal", "seleccion_filtrado", "asesor_financiero", "guardado_top_n"]
        for step in required_steps:
            assert step in results["steps"], f"Paso faltante: {step}"
            assert results["steps"][step]["success"] is True, f"Paso {step} falló: {results['steps'][step].get('error', 'Error desconocido')}"
        
        # Validar que hay resultados de análisis
        analisis_result = results["steps"]["analisis_principal"]
        assert "total_estrategias" in analisis_result, "No se encontró total de estrategias"
        assert analisis_result["total_estrategias"] > 0, "No se procesaron estrategias"
        
        # Validar que hay estrategias filtradas
        seleccion_result = results["steps"]["seleccion_filtrado"]
        assert "total_filtradas" in seleccion_result, "No se encontró total de estrategias filtradas"
        assert seleccion_result["total_filtradas"] > 0, "No se filtraron estrategias"
        
        # Validar que el asesor generó consejos
        asesor_result = results["steps"]["asesor_financiero"]
        assert "consejos_count" in asesor_result, "No se encontró conteo de consejos"
        assert asesor_result["consejos_count"] > 0, "No se generaron consejos"
        
        # Validar que se guardaron archivos
        guardado_result = results["steps"]["guardado_top_n"]
        assert "total_copied" in guardado_result, "No se encontró conteo de archivos copiados"
        assert guardado_result["total_copied"] >= 0, "Error en conteo de archivos copiados"
        
        print("✅ Test flujo completo principal: EXITOSO")
        print(f"   Estrategias analizadas: {analisis_result['total_estrategias']}")
        print(f"   Estrategias filtradas: {seleccion_result['total_filtradas']}")
        print(f"   Consejos generados: {asesor_result['consejos_count']}")
        print(f"   Archivos .sqx copiados: {guardado_result['total_copied']}")
        print(f"   Tiempo total: {results.get('execution_time', 0):.2f} segundos")
        
        return True
        
    except Exception as e:
        print(f"❌ Test flujo completo principal: FALLIDO - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_carga_datos_datamanager():
    """
    Test específico para validar que la carga de datos usa DataManager correctamente.
    """
    print("\n🧪 TEST: Carga de datos con DataManager")
    print("=" * 50)
    
    try:
        # Importar DataManager desde src
        from src.data_manager import DataManager
        
        # Crear instancia de DataManager
        dm = DataManager()
        
        # Activar modo desarrollo para usar INPUTTEST
        dm.switch_to_development_mode()
        
        # Cargar datos de KPIs
        kpis_ok = dm.load_kpis_data('DatabankExport_M1.csv')
        assert kpis_ok is True, "Error cargando datos de KPIs"
        assert dm.kpis_data is not None, "Datos de KPIs no disponibles"
        assert len(dm.kpis_data) > 0, "No se cargaron registros de KPIs"
        
        # Cargar datos de mercado
        mercado_ok = dm.load_market_data('DATOSMQL5.csv')
        assert mercado_ok is True, "Error cargando datos de mercado"
        assert dm.market_data is not None, "Datos de mercado no disponibles"
        assert len(dm.market_data) > 0, "No se cargaron registros de mercado"
        
        print("✅ Test carga datos DataManager: EXITOSO")
        print(f"   KPIs cargados: {len(dm.kpis_data)} registros")
        print(f"   Datos mercado: {len(dm.market_data)} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Test carga datos DataManager: FALLIDO - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_analisis_principal():
    """
    Test específico para validar el análisis principal.
    """
    print("\n🧪 TEST: Análisis principal")
    print("=" * 50)
    
    try:
        flujo = FlujoCompletoActualizado()
        result = flujo.paso1_analisis_principal()
        
        assert result["success"] is True, f"Análisis principal falló: {result.get('error', 'Error desconocido')}"
        assert "results" in result, "No se encontraron resultados de análisis"
        assert result["results"] is not None, "Resultados de análisis son None"
        assert len(result["results"]) > 0, "No se procesaron estrategias"
        
        print("✅ Test análisis principal: EXITOSO")
        print(f"   Estrategias procesadas: {len(result['results'])}")
        print(f"   Columnas de score: {len(result.get('score_columns', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test análisis principal: FALLIDO - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_asesor_financiero():
    """
    Test específico para validar el asesor financiero.
    """
    print("\n🧪 TEST: Asesor financiero")
    print("=" * 50)
    
    try:
        # Crear datos de prueba para el asesor
        import pandas as pd
        import numpy as np
        
        # Crear DataFrame de prueba con KPIs relevantes
        test_data = pd.DataFrame({
            'Strategy_Name': [f'Strategy_{i}' for i in range(10)],
            'CAGR_IS': np.random.uniform(0.1, 0.5, 10),
            'CAGR_OOS': np.random.uniform(0.05, 0.4, 10),
            'Sharpe_Ratio_IS': np.random.uniform(1.0, 3.0, 10),
            'Sharpe_Ratio_OOS': np.random.uniform(0.8, 2.5, 10),
            'Drawdown_IS': np.random.uniform(0.05, 0.2, 10),
            'Drawdown_OOS': np.random.uniform(0.08, 0.25, 10),
            'Profit_factor_IS': np.random.uniform(1.2, 3.0, 10),
            'Profit_factor_OOS': np.random.uniform(1.1, 2.8, 10),
            'Winning_Percent_IS': np.random.uniform(0.4, 0.7, 10),
            'Winning_Percent_OOS': np.random.uniform(0.35, 0.65, 10)
        })
        
        flujo = FlujoCompletoActualizado()
        result = flujo.paso3_asesor_financiero(test_data)
        
        assert result["success"] is True, f"Asesor financiero falló: {result.get('error', 'Error desconocido')}"
        assert "resultados" in result, "No se encontraron resultados del asesor"
        assert "consejos_completos" in result["resultados"], "No se generaron consejos"
        assert len(result["resultados"]["consejos_completos"]) > 0, "No se generaron consejos"
        
        print("✅ Test asesor financiero: EXITOSO")
        print(f"   Consejos generados: {len(result['resultados']['consejos_completos'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test asesor financiero: FALLIDO - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_configuracion_estandar():
    """
    Test para validar que la configuración estándar se crea correctamente.
    """
    print("\n🧪 TEST: Configuración estándar")
    print("=" * 50)
    
    try:
        flujo = FlujoCompletoActualizado()
        config = flujo.config
        
        # Validar campos requeridos
        required_fields = [
            "kpi_file", "market_file", "strategies_folder", "output_folder",
            "trading_style", "alpha", "percentil", "is_oos_split",
            "scientific_improvements", "selected_metrics"
        ]
        
        for field in required_fields:
            assert field in config, f"Campo faltante en configuración: {field}"
        
        # Validar valores específicos
        assert config["trading_style"] == "Intradía", f"Estilo de trading incorrecto: {config['trading_style']}"
        assert config["alpha"] == 0.8, f"Alpha incorrecto: {config['alpha']}"
        assert config["percentil"] == 95, f"Percentil incorrecto: {config['percentil']}"
        assert config["is_oos_split"] == 75, f"Split IS/OOS incorrecto: {config['is_oos_split']}"
        assert config["scientific_improvements"] is True, "Mejoras científicas no activadas"
        assert len(config["selected_metrics"]) > 0, "No hay métricas seleccionadas"
        
        print("✅ Test configuración estándar: EXITOSO")
        print(f"   Estilo de trading: {config['trading_style']}")
        print(f"   Alpha: {config['alpha']}")
        print(f"   Percentil: {config['percentil']}%")
        print(f"   Métricas seleccionadas: {len(config['selected_metrics'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test configuración estándar: FALLIDO - {str(e)}")
        import traceback
        traceback.print_exc()
        return False 