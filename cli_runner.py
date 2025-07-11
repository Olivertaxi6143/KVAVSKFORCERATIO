#!/usr/bin/env python3
"""
CLI_RUNNER.py - Interfaz de Línea de Comandos para KFORCEVSQVARATIOS

Este archivo proporciona una interfaz de línea de comandos que simula
toda la funcionalidad de la GUI pero desde la terminal.

Funcionalidades:
- Carga de datos (KPI, .sqx, mercado)
- Configuración de análisis
- Ejecución de análisis robusto
- Visualización de resultados
- Exportación de archivos
- Logging detallado con timestamps
- Testing automático
- Validación de datos mejorada

Uso:
    python cli_runner.py --help
    python cli_runner.py --config
    python cli_runner.py --run
    python cli_runner.py --auto
    python cli_runner.py --test
"""

import os
import sys
import json
import logging
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
import time
import shutil
from tqdm import tqdm
import warnings
import traceback
from contextlib import contextmanager
import gc

# Configurar warnings
warnings.filterwarnings("ignore")

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar componentes del core engine
from core_engine_enhanced import (
    ConfigManagerEnhanced,
    DataLoaderEnhanced,
    FactorKElite96Enhanced,
    QVAScorerEnhanced,
    UnifiedEvaluatorEnhanced,
    ProgressCallback,
    RobustErrorHandler,
    run_complete_analysis_with_gui_integration,
    run_unified_analysis_enhanced,
    categorize_quality,
    predictividad_is_oos_empirica
)

# Importar DataManager
from data_manager import DataManager

# Configurar logging
def setup_cli_logging():
    """Configura el sistema de logging para CLI."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"cli_run_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_filename

class DataValidator:
    """Validador robusto de datos para CLI."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_columns = [
            'Strategy', 'CAGR', 'Sharpe_Ratio', 'Max_Drawdown',
            'Profit_Factor', 'Total_Return', 'Win_Rate'
        ]
        self.optional_columns = [
            'Calmar_Ratio', 'Sortino_Ratio', 'Recovery_Factor',
            'Risk_Adjusted_Return', 'Volatility'
        ]
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida que el DataFrame tenga la estructura correcta."""
        errors = []
        
        # Verificar que no esté vacío
        if df.empty:
            errors.append("DataFrame está vacío")
            return False, errors
        
        # Verificar columnas requeridas
        missing_required = [col for col in self.required_columns if col not in df.columns]
        if missing_required:
            errors.append(f"Columnas requeridas faltantes: {missing_required}")
        
        # Verificar tipos de datos
        numeric_errors = self._validate_numeric_columns(df)
        errors.extend(numeric_errors)
        
        # Verificar valores extremos
        outlier_errors = self._validate_outliers(df)
        errors.extend(outlier_errors)
        
        return len(errors) == 0, errors
    
    def _validate_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """Valida que las columnas numéricas tengan tipos correctos."""
        errors = []
        
        for col in self.required_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"Columna {col} no es numérica")
                elif df[col].isna().sum() > len(df) * 0.5:  # Más del 50% NaN
                    errors.append(f"Columna {col} tiene demasiados valores faltantes")
        
        return errors
    
    def _validate_outliers(self, df: pd.DataFrame) -> List[str]:
        """Valida valores extremos en columnas numéricas."""
        errors = []
        
        for col in self.required_columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                # Detectar outliers usando IQR
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                if len(outliers) > len(df) * 0.1:  # Más del 10% outliers
                    errors.append(f"Columna {col} tiene muchos valores extremos ({len(outliers)} outliers)")
        
        return errors

class CLIRunner:
    """Clase principal para ejecutar el análisis desde CLI."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManagerEnhanced()
        self.data_loader = DataLoaderEnhanced()
        self.error_handler = RobustErrorHandler()
        self.progress_callback = ProgressCallback()
        self.data_validator = DataValidator()
        
        # Configuración por defecto
        self.default_config = {
            "kpi_file": "DatabankExport_M1.csv",
            "sqx_folder": "INPUTTEST/M1_NDX_UP_MQL4_136_STOP",
            "market_file": "DATOSMQL5.csv",
            "output_folder": "INPUTTEST/TOP",
            "trading_style": "Intradía",
            "alpha": 0.8,
            "top_n": 20,
            "percentil": 80.0,
            "scientific_improvements": False,
            "analysis_type": "unified",
            "is_oos_split": 0.75,
            "auto_export": True,
            "create_backup": True,
            "validate_data": True,
            "max_retries": 3
        }
        
        self.current_config = self.default_config.copy()
        self.results_df = None
        self.summary = None
        self.start_time = None
        
    @contextmanager
    def error_context(self, operation: str):
        """Context manager para manejo robusto de errores."""
        try:
            self.logger.info(f"🔄 Iniciando: {operation}")
            yield
            self.logger.info(f"✅ Completado: {operation}")
        except Exception as e:
            self.logger.error(f"❌ Error en {operation}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def load_config_from_file(self, config_file: str = "cli_config.json") -> bool:
        """Carga configuración desde archivo JSON."""
        with self.error_context("Carga de configuración"):
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.current_config.update(loaded_config)
                    self.logger.info(f"Configuración cargada desde {config_file}")
                    return True
            else:
                self.logger.warning(f"Archivo de configuración {config_file} no encontrado")
                return False
    
    def save_config_to_file(self, config_file: str = "cli_config.json") -> bool:
        """Guarda la configuración actual en archivo JSON."""
        with self.error_context("Guardado de configuración"):
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuración guardada en {config_file}")
            return True
    
    def validate_files(self) -> bool:
        """Valida que todos los archivos necesarios existan."""
        with self.error_context("Validación de archivos"):
            self.logger.info("🔍 Validando archivos...")
            
            files_to_check = [
                ("Archivo KPI", self.current_config["kpi_file"]),
                ("Carpeta .sqx", self.current_config["sqx_folder"]),
                ("Archivo de mercado", self.current_config["market_file"])
            ]
            
            all_valid = True
            for name, path in files_to_check:
                if os.path.exists(path):
                    size = os.path.getsize(path) if os.path.isfile(path) else "Carpeta"
                    self.logger.info(f"✅ {name}: {path} ({size} bytes)")
                else:
                    self.logger.error(f"❌ {name} no encontrado: {path}")
                    all_valid = False
            
            # Crear carpeta de salida si no existe
            output_folder = self.current_config["output_folder"]
            if not os.path.exists(output_folder):
                try:
                    os.makedirs(output_folder)
                    self.logger.info(f"📁 Carpeta de salida creada: {output_folder}")
                except Exception as e:
                    self.logger.error(f"❌ Error creando carpeta de salida: {e}")
                    all_valid = False
            
            return all_valid
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Carga y prepara los datos usando DataManager, asegurando mapeo y limpieza de columnas."""
        with self.error_context("Carga de datos"):
            self.logger.info("📊 Cargando datos...")
            
            # Usar DataManager para cargar y normalizar datos
            dm = DataManager()
            kpi_file = self.current_config["kpi_file"]
            self.logger.info(f"Cargando archivo KPI: {kpi_file} (vía DataManager)")
            
            # Cargar y normalizar datos de KPIs
            dm.load_kpis_data(kpi_file)
            df = dm.kpis_data
            if df is None or df.empty:
                self.logger.error("❌ No se pudieron cargar los datos de KPIs desde DataManager")
                return None
            
            self.logger.info(f"✅ Datos cargados y normalizados: {len(df)} estrategias")
            
            # Validar datos si está habilitado
            if self.current_config.get("validate_data", True):
                is_valid, errors = self.data_validator.validate_dataframe(df)
                if not is_valid:
                    self.logger.warning("⚠️ Problemas detectados en los datos:")
                    for error in errors:
                        self.logger.warning(f"  - {error}")
                else:
                    self.logger.info("✅ Validación de datos exitosa")
            
            # Aplicar mejoras de manejo de datos faltantes
            df = self._improve_missing_data_handling(df)
            
            return df
    
    def _check_column_nulls(self, data: Union[pd.Series, pd.DataFrame]) -> bool:
        """Función auxiliar para verificar valores nulos en una columna de forma segura."""
        if isinstance(data, pd.Series):
            return data.isna().any()
        elif isinstance(data, pd.DataFrame):
            return data.isna().any().any()
        else:
            return False
    
    def _improve_missing_data_handling(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mejora el manejo de datos faltantes en el DataFrame.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            DataFrame con datos faltantes manejados apropiadamente
        """
        try:
            self.logger.info("Mejorando manejo de datos faltantes...")
            
            # Crear una copia para no modificar el original
            df_improved = df.copy()
            
            # Identificar columnas numéricas
            numeric_columns = df_improved.select_dtypes(include=[np.number]).columns
            
            # Para columnas numéricas, usar métodos apropiados de imputación
            for col in numeric_columns:
                if self._check_column_nulls(df_improved[col]):
                    # Para métricas de rendimiento, usar mediana (más robusta)
                    if any(metric in col.lower() for metric in ['cagr', 'profit', 'sharpe', 'return']):
                        df_improved[col] = df_improved[col].fillna(df_improved[col].median())
                    # Para métricas de riesgo, usar percentil 75 (conservador)
                    elif any(metric in col.lower() for metric in ['drawdown', 'risk', 'var', 'cvar']):
                        df_improved[col] = df_improved[col].fillna(df_improved[col].quantile(0.75))
                    # Para otras métricas numéricas, usar media
                    else:
                        df_improved[col] = df_improved[col].fillna(df_improved[col].mean())
            
            # Para columnas categóricas, usar moda o valor por defecto
            categorical_columns = df_improved.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                if self._check_column_nulls(df_improved[col]):
                    mode_value = df_improved[col].mode()
                    if not mode_value.empty:
                        df_improved[col] = df_improved[col].fillna(mode_value.iloc[0])
                    else:
                        df_improved[col] = df_improved[col].fillna("N/A")
            
            # Verificar que no queden valores NaN
            remaining_nans = df_improved.isna().sum().sum()
            if remaining_nans > 0:
                self.logger.warning(f"Quedan {remaining_nans} valores NaN después de la imputación")
                # Imputación final con valores por defecto
                df_improved = df_improved.fillna(0)
            
            self.logger.info("Manejo de datos faltantes completado exitosamente")
            return df_improved
        except Exception as e:
            self.logger.error(f"❌ Error en _improve_missing_data_handling: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return df
    
    def run_analysis(self) -> bool:
        """Ejecuta el análisis completo."""
        with self.error_context("Ejecución de análisis"):
            self.logger.info("🚀 Iniciando análisis robusto...")
            self.start_time = time.time()
            
            # Cargar datos
            df = self.load_data()
            if df is None or df.empty:
                self.logger.error("❌ No se pudieron cargar los datos")
                return False
            
            # Preparar configuración de análisis
            config = {
                "trading_style": self.current_config["trading_style"],
                "alpha": self.current_config["alpha"],
                "top_n": self.current_config["top_n"],
                "percentil": self.current_config["percentil"],
                "scientific_improvements": self.current_config["scientific_improvements"],
                "analysis_type": self.current_config["analysis_type"],
                "is_oos_split": self.current_config["is_oos_split"]
            }
            
            self.logger.info(f"⚙️ Configuración: {config}")
            
            # Ejecutar análisis con reintentos
            max_retries = self.current_config.get("max_retries", 3)
            for attempt in range(max_retries):
                try:
                    if config["analysis_type"] == "unified":
                        self.logger.info("🔬 Ejecutando análisis Unified...")
                        results, summary = run_unified_analysis_enhanced(
                            df, 
                            config=config, 
                            progress_callback=self.progress_callback
                        )
                    else:
                        self.logger.info("🔬 Ejecutando análisis Factor K...")
                        results = run_complete_analysis_with_gui_integration(
                            self.current_config["kpi_file"],
                            config=config,
                            progress_callback=self.progress_callback,
                            analysis_type=config["analysis_type"]
                        )
                        summary = {}
                    
                    # Verificar que results sea un DataFrame válido
                    if results is None:
                        raise ValueError("No se obtuvieron resultados del análisis")
                    if hasattr(results, 'empty') and results.empty:
                        raise ValueError("DataFrame de resultados está vacío")
                    
                    break  # Si llegamos aquí, el análisis fue exitoso
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Intento {attempt + 1}/{max_retries} falló: {e}")
                    if attempt == max_retries - 1:
                        self.logger.error("❌ Todos los intentos fallaron")
                        return False
                    time.sleep(2)  # Esperar antes del siguiente intento
            
            # Aplicar categorización de calidad (results ya es DataFrame aquí)
            self.logger.info(f"Tipo de results antes de categorize_quality: {type(results)}")
            results = categorize_quality(results)
            self.logger.info(f"Tipo de results después de categorize_quality: {type(results)}")
            
            # Aplicar análisis IS/OOS (results ya es DataFrame aquí)
            self.logger.info(f"Tipo de results antes de predictividad_is_oos_empirica: {type(results)}")
            results = predictividad_is_oos_empirica(results, config["is_oos_split"])
            self.logger.info(f"Tipo de results después de predictividad_is_oos_empirica: {type(results)}")
            
            # Filtrar por percentil
            if "Unified_Score" in results.columns:
                score_col = "Unified_Score"
            elif "QVA_Score" in results.columns:
                score_col = "QVA_Score"
            else:
                score_col = "Score"
            
            if score_col in results.columns:
                percentile_value = results[score_col].quantile(self.current_config["percentil"] / 100)
                filtered_results = results[results[score_col] >= percentile_value]
                self.logger.info(f"📊 Filtrado por percentil {self.current_config['percentil']}: {len(filtered_results)} estrategias")
            else:
                filtered_results = results
                self.logger.warning("⚠️ No se encontró columna de score para filtrar")
            
            # Ordenar por score
            if score_col in filtered_results.columns:
                filtered_results = filtered_results.sort_values(by=score_col, ascending=False)
            
            self.results_df = filtered_results
            self.summary = summary
            
            # Calcular tiempo de ejecución
            execution_time = time.time() - self.start_time
            self.logger.info(f"✅ Análisis completado en {execution_time:.2f} segundos: {len(filtered_results)} estrategias procesadas")
            return True
    
    def run_automated_test(self) -> bool:
        """Ejecuta pruebas automatizadas del flujo completo."""
        with self.error_context("Testing automatizado"):
            self.logger.info("🧪 Iniciando pruebas automatizadas...")
            
            test_results = {
                "file_validation": False,
                "data_loading": False,
                "analysis_execution": False,
                "results_validation": False,
                "export_functionality": False
            }
            
            # Test 1: Validación de archivos
            self.logger.info("📋 Test 1: Validación de archivos...")
            test_results["file_validation"] = self.validate_files()
            
            # Test 2: Carga de datos
            self.logger.info("📊 Test 2: Carga de datos...")
            df = self.load_data()
            test_results["data_loading"] = df is not None and not df.empty
            
            # Test 3: Ejecución de análisis
            self.logger.info("🔬 Test 3: Ejecución de análisis...")
            test_results["analysis_execution"] = self.run_analysis()
            
            # Test 4: Validación de resultados
            self.logger.info("✅ Test 4: Validación de resultados...")
            if self.results_df is not None and not self.results_df.empty:
                test_results["results_validation"] = True
                self.logger.info(f"  - Estrategias procesadas: {len(self.results_df)}")
                self.logger.info(f"  - Columnas disponibles: {list(self.results_df.columns)}")
            
            # Test 5: Funcionalidad de exportación
            self.logger.info("💾 Test 5: Funcionalidad de exportación...")
            test_results["export_functionality"] = self.export_results()
            
            # Mostrar resumen de pruebas
            self.logger.info("\n" + "="*50)
            self.logger.info("📋 RESUMEN DE PRUEBAS AUTOMATIZADAS")
            self.logger.info("="*50)
            
            passed_tests = sum(test_results.values())
            total_tests = len(test_results)
            
            for test_name, result in test_results.items():
                status = "✅ PASÓ" if result else "❌ FALLÓ"
                self.logger.info(f"  {test_name}: {status}")
            
            self.logger.info(f"\n🎯 Resultado: {passed_tests}/{total_tests} pruebas pasaron")
            
            if passed_tests == total_tests:
                self.logger.info("🎉 ¡Todas las pruebas pasaron exitosamente!")
                return True
            else:
                self.logger.warning("⚠️ Algunas pruebas fallaron")
                return False
    
    def display_results(self):
        """Muestra los resultados en formato tabular."""
        if self.results_df is None or self.results_df.empty:
            self.logger.warning("⚠️ No hay resultados para mostrar")
            return
        
        with self.error_context("Visualización de resultados"):
            self.logger.info("\n" + "="*80)
            self.logger.info("📊 RESULTADOS DEL ANÁLISIS")
            self.logger.info("="*80)
            
            # Mostrar top estrategias
            top_n = min(self.current_config["top_n"], len(self.results_df))
            top_strategies = self.results_df.head(top_n)
            
            # Determinar columna de score
            score_col = None
            for col in ["Unified_Score", "QVA_Score", "Score"]:
                if col in self.results_df.columns:
                    score_col = col
                    break
            
            if score_col:
                self.logger.info(f"🏆 TOP {top_n} ESTRATEGIAS (por {score_col})")
                self.logger.info("-" * 80)
                
                # Mostrar columnas principales
                display_columns = ["Strategy", score_col]
                if "CAGR" in self.results_df.columns:
                    display_columns.append("CAGR")
                if "Sharpe_Ratio" in self.results_df.columns:
                    display_columns.append("Sharpe_Ratio")
                if "Max_Drawdown" in self.results_df.columns:
                    display_columns.append("Max_Drawdown")
                if "Quality_Category" in self.results_df.columns:
                    display_columns.append("Quality_Category")
                
                # Mostrar tabla
                for idx, row in top_strategies[display_columns].iterrows():
                    strategy = row["Strategy"]
                    score = f"{row[score_col]:.4f}" if pd.notna(row[score_col]) else "N/A"
                    
                    line = f"{strategy:<30} | {score:>10}"
                    if "CAGR" in display_columns:
                        cagr = f"{row['CAGR']:.2f}%" if pd.notna(row['CAGR']) else "N/A"
                        line += f" | {cagr:>8}"
                    if "Sharpe_Ratio" in display_columns:
                        sharpe = f"{row['Sharpe_Ratio']:.2f}" if pd.notna(row['Sharpe_Ratio']) else "N/A"
                        line += f" | {sharpe:>8}"
                    if "Max_Drawdown" in display_columns:
                        dd = f"{row['Max_Drawdown']:.2f}%" if pd.notna(row['Max_Drawdown']) else "N/A"
                        line += f" | {dd:>8}"
                    if "Quality_Category" in display_columns:
                        quality = row["Quality_Category"] if pd.notna(row["Quality_Category"]) else "N/A"
                        line += f" | {quality:>12}"
                    
                    self.logger.info(line)
            
            # Mostrar estadísticas generales
            self.logger.info("\n📈 ESTADÍSTICAS GENERALES")
            self.logger.info("-" * 40)
            self.logger.info(f"Total de estrategias: {len(self.results_df)}")
            
            if score_col:
                scores = self.results_df[score_col].dropna()
                if len(scores) > 0:
                    self.logger.info(f"Score promedio: {scores.mean():.4f}")
                    self.logger.info(f"Score máximo: {scores.max():.4f}")
                    self.logger.info(f"Score mínimo: {scores.min():.4f}")
                    self.logger.info(f"Desviación estándar: {scores.std():.4f}")
            
            # Mostrar distribución de calidad si existe
            if "Quality_Category" in self.results_df.columns:
                quality_dist = self.results_df["Quality_Category"].value_counts()
                self.logger.info("\n🏷️ DISTRIBUCIÓN DE CALIDAD")
                self.logger.info("-" * 30)
                for quality, count in quality_dist.items():
                    percentage = (count / len(self.results_df)) * 100
                    self.logger.info(f"{quality}: {count} ({percentage:.1f}%)")
    
    def export_results(self):
        """Exporta los resultados a archivos."""
        if self.results_df is None or self.results_df.empty:
            self.logger.warning("⚠️ No hay resultados para exportar")
            return False
        
        with self.error_context("Exportación de resultados"):
            self.logger.info("💾 Exportando resultados...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = self.current_config["output_folder"]
            
            # Crear backup si está habilitado
            if self.current_config.get("create_backup", True):
                backup_folder = os.path.join(output_folder, f"backup_{timestamp}")
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                self.logger.info(f"📦 Creando backup en: {backup_folder}")
            
            # Exportar resultados principales
            results_file = os.path.join(output_folder, f"resultados_analisis_{timestamp}.csv")
            self.results_df.to_csv(results_file, index=False, encoding='utf-8')
            self.logger.info(f"✅ Resultados exportados: {results_file}")
            
            # Exportar top estrategias
            top_n = min(self.current_config["top_n"], len(self.results_df))
            top_file = os.path.join(output_folder, f"top_{top_n}_estrategias_{timestamp}.csv")
            self.results_df.head(top_n).to_csv(top_file, index=False, encoding='utf-8')
            self.logger.info(f"✅ Top {top_n} estrategias exportadas: {top_file}")
            
            # Exportar resumen en formato JSON
            if self.summary:
                summary_file = os.path.join(output_folder, f"resumen_analisis_{timestamp}.json")
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(self.summary, f, indent=2, ensure_ascii=False)
                self.logger.info(f"✅ Resumen exportado: {summary_file}")
            
            # Exportar configuración utilizada
            config_file = os.path.join(output_folder, f"configuracion_{timestamp}.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Configuración exportada: {config_file}")
            
            # Copiar archivos .sqx si está habilitado
            if self.current_config.get("copy_sqx_files", True):
                self.copy_sqx_files()
            
            return True
    
    def copy_sqx_files(self):
        """Copia los archivos .sqx de las mejores estrategias."""
        if self.results_df is None or self.results_df.empty:
            self.logger.warning("⚠️ No hay resultados para copiar archivos .sqx")
            return
        
        with self.error_context("Copia de archivos .sqx"):
            self.logger.info("📁 Copiando archivos .sqx de mejores estrategias...")
            
            sqx_folder = self.current_config["sqx_folder"]
            output_folder = self.current_config["output_folder"]
            top_n = min(self.current_config["top_n"], len(self.results_df))
            
            # Crear carpeta para archivos .sqx
            sqx_output_folder = os.path.join(output_folder, "mejores_estrategias")
            if not os.path.exists(sqx_output_folder):
                os.makedirs(sqx_output_folder)
            
            copied_count = 0
            for idx, row in self.results_df.head(top_n).iterrows():
                strategy_name = row["Strategy_Name"]
                
                # Buscar archivo .sqx correspondiente
                sqx_file = None
                for file in os.listdir(sqx_folder):
                    if file.endswith('.sqx') and strategy_name in file:
                        sqx_file = os.path.join(sqx_folder, file)
                        break
                
                if sqx_file and os.path.exists(sqx_file):
                    # Copiar archivo
                    dest_file = os.path.join(sqx_output_folder, f"{strategy_name}.sqx")
                    shutil.copy2(sqx_file, dest_file)
                    copied_count += 1
                    self.logger.info(f"  ✅ Copiado: {strategy_name}")
                else:
                    self.logger.warning(f"  ⚠️ No encontrado: {strategy_name}")
            
            self.logger.info(f"📁 Copiados {copied_count} archivos .sqx a: {sqx_output_folder}")
    
    def show_summary(self):
        """Muestra un resumen completo del análisis."""
        if self.results_df is None or self.results_df.empty:
            self.logger.warning("⚠️ No hay resultados para mostrar resumen")
            return
        
        with self.error_context("Generación de resumen"):
            self.logger.info("\n" + "="*80)
            self.logger.info("📋 RESUMEN COMPLETO DEL ANÁLISIS")
            self.logger.info("="*80)
            
            # Información general
            self.logger.info(f"📊 Total de estrategias analizadas: {len(self.results_df)}")
            self.logger.info(f"⚙️ Configuración utilizada:")
            for key, value in self.current_config.items():
                self.logger.info(f"  - {key}: {value}")
            
            # Tiempo de ejecución
            if self.start_time:
                execution_time = time.time() - self.start_time
                self.logger.info(f"⏱️ Tiempo de ejecución: {execution_time:.2f} segundos")
            
            # Estadísticas de scores
            score_col = None
            for col in ["Unified_Score", "QVA_Score", "Score"]:
                if col in self.results_df.columns:
                    score_col = col
                    break
            
            if score_col:
                scores = self.results_df[score_col].dropna()
                if len(scores) > 0:
                    self.logger.info(f"\n📈 Estadísticas de {score_col}:")
                    self.logger.info(f"  - Promedio: {scores.mean():.4f}")
                    self.logger.info(f"  - Mediana: {scores.median():.4f}")
                    self.logger.info(f"  - Máximo: {scores.max():.4f}")
                    self.logger.info(f"  - Mínimo: {scores.min():.4f}")
                    self.logger.info(f"  - Desviación estándar: {scores.std():.4f}")
            
            # Distribución de calidad
            if "Quality_Category" in self.results_df.columns:
                quality_dist = self.results_df["Quality_Category"].value_counts()
                self.logger.info(f"\n🏷️ Distribución de calidad:")
                for quality, count in quality_dist.items():
                    percentage = (count / len(self.results_df)) * 100
                    self.logger.info(f"  - {quality}: {count} ({percentage:.1f}%)")
            
            # Mejores estrategias
            top_n = min(5, len(self.results_df))
            self.logger.info(f"\n🏆 Top {top_n} estrategias:")
            for idx, row in self.results_df.head(top_n).iterrows():
                strategy = row["Strategy_Name"]
                score = f"{row[score_col]:.4f}" if score_col and pd.notna(row[score_col]) else "N/A"
                self.logger.info(f"  {idx+1}. {strategy} (Score: {score})")
            
            # Información de archivos generados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = self.current_config["output_folder"]
            self.logger.info(f"\n💾 Archivos generados en: {output_folder}")
            self.logger.info(f"  - resultados_analisis_{timestamp}.csv")
            self.logger.info(f"  - top_{top_n}_estrategias_{timestamp}.csv")
            self.logger.info(f"  - resumen_analisis_{timestamp}.json")
            self.logger.info(f"  - configuracion_{timestamp}.json")
            
            # Limpieza de memoria
            gc.collect()
            self.logger.info("🧹 Memoria liberada")

def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="CLI para KFORCEVSQVARATIOS - Análisis robusto de estrategias de trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python cli_runner.py --config                    # Configurar parámetros
  python cli_runner.py --run                      # Ejecutar análisis
  python cli_runner.py --auto                     # Ejecutar con configuración automática
  python cli_runner.py --test                     # Ejecutar pruebas automatizadas
  python cli_runner.py --validate                 # Validar archivos
  python cli_runner.py --export                   # Exportar resultados
        """
    )
    
    parser.add_argument("--config", action="store_true", help="Configurar parámetros interactivamente")
    parser.add_argument("--run", action="store_true", help="Ejecutar análisis completo")
    parser.add_argument("--auto", action="store_true", help="Ejecutar con configuración automática")
    parser.add_argument("--test", action="store_true", help="Ejecutar pruebas automatizadas")
    parser.add_argument("--validate", action="store_true", help="Validar archivos de entrada")
    parser.add_argument("--export", action="store_true", help="Exportar resultados")
    parser.add_argument("--config-file", default="cli_config.json", help="Archivo de configuración")
    parser.add_argument("--kpi-file", help="Archivo KPI")
    parser.add_argument("--sqx-folder", help="Carpeta con archivos .sqx")
    parser.add_argument("--market-file", help="Archivo de mercado")
    parser.add_argument("--output-folder", help="Carpeta de salida")
    parser.add_argument("--trading-style", choices=["Intradía", "Swing", "Tendencial", "Reversión", "Breakout"], help="Estilo de trading")
    parser.add_argument("--alpha", type=float, help="Parámetro alpha (0.0-1.0)")
    parser.add_argument("--top-n", type=int, help="Número de estrategias top")
    parser.add_argument("--percentil", type=float, help="Percentil de filtrado")
    parser.add_argument("--scientific", action="store_true", help="Habilitar mejoras científicas")
    parser.add_argument("--no-validate", action="store_true", help="Deshabilitar validación de datos")
    parser.add_argument("--no-backup", action="store_true", help="No crear backups")
    parser.add_argument("--max-retries", type=int, default=3, help="Máximo número de reintentos")
    
    args = parser.parse_args()
    
    # Configurar logging
    log_filename = setup_cli_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Iniciando CLI Runner para KFORCEVSQVARATIOS")
    logger.info(f"📝 Log guardado en: {log_filename}")
    
    try:
        # Crear instancia del CLI
        cli = CLIRunner()
        
        # Cargar configuración
        cli.load_config_from_file(args.config_file)
        
        # Aplicar argumentos de línea de comandos
        if args.kpi_file:
            cli.current_config["kpi_file"] = args.kpi_file
        if args.sqx_folder:
            cli.current_config["sqx_folder"] = args.sqx_folder
        if args.market_file:
            cli.current_config["market_file"] = args.market_file
        if args.output_folder:
            cli.current_config["output_folder"] = args.output_folder
        if args.trading_style:
            cli.current_config["trading_style"] = args.trading_style
        if args.alpha is not None:
            cli.current_config["alpha"] = args.alpha
        if args.top_n is not None:
            cli.current_config["top_n"] = args.top_n
        if args.percentil is not None:
            cli.current_config["percentil"] = args.percentil
        if args.scientific:
            cli.current_config["scientific_improvements"] = True
        if args.no_validate:
            cli.current_config["validate_data"] = False
        if args.no_backup:
            cli.current_config["create_backup"] = False
        if args.max_retries:
            cli.current_config["max_retries"] = args.max_retries
        
        # Ejecutar según argumentos
        success = False
        
        if args.config:
            logger.info("⚙️ Modo configuración interactiva")
            # Aquí podrías agregar configuración interactiva
            cli.save_config_to_file(args.config_file)
            logger.info("✅ Configuración guardada")
            success = True
            
        elif args.validate:
            logger.info("🔍 Modo validación de archivos")
            success = cli.validate_files()
            
        elif args.test:
            logger.info("🧪 Modo testing automatizado")
            success = cli.run_automated_test()
            
        elif args.auto:
            logger.info("🤖 Modo automático")
            if cli.validate_files():
                if cli.run_analysis():
                    cli.display_results()
                    if cli.current_config.get("auto_export", True):
                        cli.export_results()
                    cli.show_summary()
                    success = True
                else:
                    logger.error("❌ Error en análisis automático")
            else:
                logger.error("❌ Error en validación de archivos")
                
        elif args.run:
            logger.info("🚀 Modo ejecución manual")
            if cli.validate_files():
                if cli.run_analysis():
                    cli.display_results()
                    cli.show_summary()
                    success = True
                else:
                    logger.error("❌ Error en análisis")
            else:
                logger.error("❌ Error en validación de archivos")
                
        elif args.export:
            logger.info("💾 Modo exportación")
            if cli.results_df is not None and not cli.results_df.empty:
                success = cli.export_results()
                if success:
                    cli.show_summary()
            else:
                logger.error("❌ No hay resultados para exportar")
                
        else:
            # Modo por defecto: mostrar ayuda
            parser.print_help()
            success = True
        
        # Mostrar resultado final
        if success:
            logger.info("✅ Operación completada exitosamente")
        else:
            logger.error("❌ Operación falló")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        # Limpieza final
        try:
            gc.collect()
            logger.info("🧹 Limpieza final completada")
        except:
            pass

if __name__ == "__main__":
    main() 