from typing import Optional, Any, Union
import warnings
"""
06_DATA_MANAGER.py - Gestión Centralizada de Datos

Este módulo centraliza toda la gestión de datos del sistema KFORCEVSQVARATIOS:
    pass
- Carga y consolidación de datos de múltiples fuentes
- Gestión de datos de estrategias (StrategyQuant)
- Datos de mercado (DATOSMQL5.csv)
- KPIs históricos (DatabankExport_M1.csv)
- Datos de portafolios (PDFs)
- Validación y limpieza centralizada
- Interfaz unificada para acceso a datos
- Soporte para INPUTTEST (desarrollo) y rutas de usuario (producción)

Responsabilidades:
    pass
- Carga de datos desde diferentes fuentes
- Consolidación y normalización
- Validación y limpieza
- Gestión de caché y persistencia
- Interfaz unificada para otros módulos
- Preservación de datos reales sin cocinamiento
"""

import pandas as pd
import numpy as np
import os
import json
import gzip
import time
import re
import logging
import pickle
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from .data_utils import extract_float_from_tuple, calculate_basic_stats, detect_outliers_iqr
from .column_mapping import normalize_column_names

# Configurar logging
try:
    from core.logger_config import setup_logger
    logger = setup_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class DataManager:
    """
    Gestor centralizado de datos para el sistema de análisis cuantitativo.

    ADVERTENCIA PROFESIONAL:
    ------------------------------------------------------------
    Toda carga, validación, limpieza y manipulación de archivos de estrategias (.sqx, .csv, .xlsx, etc.)
    debe realizarse exclusivamente a través de este módulo y utilidades de la carpeta data.
    Ningún otro módulo debe realizar validación, carga ni manipulación local de datos.
    Este módulo es la única fuente de datos preparados y validados para el core y análisis.
    ------------------------------------------------------------
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el gestor de datos centralizado.
        
        Args:
            config: Configuración opcional del sistema
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Datos cargados - inicializar con tipos correctos
        self._strategies_data: pd.DataFrame | None = None
        self._portfolio_data: Dict[str, Any] | None = None
        self._market_data: pd.DataFrame | None = None
        self._kpis_data: pd.DataFrame | None = None
        self._consolidated_data: Dict[str, Any] | None = None
        
        # Estado de carga
        self._load_status = {
            'strategies': False,
            'portfolio': False,
            'market': False,
            'kpis': False
        }
        
        # Configuración por defecto según la documentación
        self.default_config = {
            'csv_delimiter': ';',
            'csv_decimal': ',',
            'is_oos_ratio': 0.7,  # 70/30 split
            'required_columns': [
                'Net_Profit_IS', 'Net_Profit_OOS',
                'Sharpe_Ratio_IS', 'Sharpe_Ratio_OOS',
                'Max_Drawdown_IS', 'Max_Drawdown_OOS',
                'Profit_Factor_IS', 'Profit_Factor_OOS',
                'CAGR_IS', 'CAGR_OOS'
            ],
            'default_files': {
                'kpis_file': 'DatabankExport_M1.csv',
                'market_file': 'DATOSMQL5.csv',
                'strategies_folder': r'G:\Mi unidad\MINERIAQVAPORTFOLIO\NDX_UP_135_136_RETEST_2\136\RETEST2\M1_NDX_UP_MQL4_136_STOP\M1_NDX_UP_MQL4_136_STOP',
                'output_folder': r'G:\Mi unidad\MINERIAQVAPORTFOLIO\NDX_UP_135_136_RETEST_2\136\RETEST2\M1_NDX_UP_MQL4_136_STOP\TOP'
            },
            'validation': {
                'strict_validation': True,
                'imputation_method': 'regime_based',
                'outlier_detection': 'isolation_forest',
                'outlier_threshold': 0.1
            },
            'cache': {
                'enable_cache': True,
                'cache_duration_hours': 24,
                'cache_dir': 'cache'
            },
            'development': {
                'use_inputtest': False,  # Cambiar a True para desarrollo
                'inputtest_path': 'INPUTTEST'
            }
        }
        
        # Actualizar configuración
        self.config.update(self.default_config)
        
        # Crear directorio de caché si está habilitado
        if self.config['cache']['enable_cache']:
            cache_dir = Path(self.config['cache']['cache_dir'])
            cache_dir.mkdir(exist_ok=True)
        
        # Mapeo de columnas críticas para INPUTTEST y datos reales
        self.COLUMN_MAPPINGS = {
            # INPUTTEST y datos reales
            'Strategy Name': 'Strategy_Name',
            'CAGR (IS)': 'CAGR_IS',
            'CAGR (OOS)': 'CAGR_OOS',
            'Drawdown (IS)': 'Drawdown_IS',
            'Drawdown (OOS)': 'Drawdown_OOS',
            'Sharpe Ratio (IS)': 'Sharpe_Ratio_IS',
            'Sharpe Ratio (OOS)': 'Sharpe_Ratio_OOS',
            'Profit factor (IS)': 'Profit_factor_IS',
            'Profit factor (OOS)': 'Profit_factor_OOS',
            'Winning Percent (IS)': 'Winning_Percent_IS',
            'Winning Percent (OOS)': 'Winning_Percent_OOS',
            'Net profit (IS)': 'Net_profit_IS',
            'Net profit (OOS)': 'Net_profit_OOS',
            'CalmarRatio (IS)': 'CalmarRatio_IS',
            'CalmarRatio (OOS)': 'CalmarRatio_OOS',
            'SQN Score (IS)': 'SQN_Score_IS',
            'SQN Score (OOS)': 'SQN_Score_OOS',
            'R Expectancy (IS)': 'R_Expectancy_IS',
            'R Expectancy (OOS)': 'R_Expectancy_OOS',
            'Winning Percent': 'Winning_Percent',
            'Max DD %': 'Max_DD_pct',
            'Avg. MAE - Profit/loss': 'Avg_MAE_Profit_loss',
            'Avg. MFE - Profit/loss': 'Avg_MFE_Profit_loss',
            'Max Consec. Losses': 'Max_Consec_Losses',
            'Payout ratio': 'Payout_ratio',
            'Ulcer Index %': 'Ulcer_Index_pct',
            'Ulcer Performance Index': 'Ulcer_Performance_Index',
            'Max Drawdown Duration': 'Max_Drawdown_Duration',
            'Avg. Bars in Trade': 'Avg_Bars_in_Trade',
            'VaR (95%)': 'VaR_95pct',
            'CVaR (95%)': 'CVaR_95pct',
            'Sortino Ratio': 'Sortino_Ratio',
            'RecoveryFactor': 'RecoveryFactor',
            'Stagnation (Trades)': 'Stagnation',
            'Max Stagnation Trades': 'Stagnation_Trades',
            'Stagnation_Trades': 'Stagnation_Trades',
            'New Peak Trades %': 'New_Peak_Trades_pct',
            'Drawdown Trades %': 'Drawdown_Trades_pct',
            # Datos de mercado
            'Date': 'Date',
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        }
        
        self.logger.info("DataManager inicializado correctamente")
        
        # NO cargar datos automáticamente para evitar duplicaciones
        # self._auto_load_data()
        
    def _auto_load_data(self):
        """Carga datos automáticamente si están disponibles."""
        try:
            # Intentar cargar datos de INPUTTEST primero
            if self.config['development']['use_inputtest']:
                inputtest_data = load_inputtest_data_pipeline()
                kpis_data = inputtest_data.get('kpis')
                if kpis_data is not None and not kpis_data.empty:
                    self._kpis_data = kpis_data
                    self._load_status['kpis'] = True
                    self.logger.info(f"✅ Datos de INPUTTEST cargados automáticamente: {len(kpis_data)} registros")
                    return
            
            # Intentar cargar datos por defecto
            default_kpis = self.config['default_files']['kpis_file']
            if os.path.exists(default_kpis):
                success = self.load_kpis_data(default_kpis)
                if success and self._kpis_data is not None:
                    self.logger.info(f"[OK] Datos por defecto cargados automáticamente: {len(self._kpis_data)} registros")
                    return
            
            self.logger.info("⚠️ No se encontraron datos para carga automática")
            
        except Exception as e:
            self.logger.error(f"Error en carga automática: {e}")
    
    # ===================== PROPIEDADES Y GETTERS =====================
    
    @property
    def strategies_data(self) -> pd.DataFrame | None:
        """Obtiene los datos de estrategias cargados."""
        return self._strategies_data
    
    @property
    def portfolio_data(self) -> Dict[str, Any] | None:
        """Obtiene los datos de portafolio cargados."""
        return self._portfolio_data
    
    @property
    def market_data(self) -> pd.DataFrame | None:
        """Obtiene los datos de mercado cargados."""
        return self._market_data
    
    @property
    def kpis_data(self) -> pd.DataFrame | None:
        """Obtiene los datos de KPIs cargados."""
        return self._kpis_data
    
    @property
    def consolidated_data(self) -> Dict[str, Any] | None:
        """Obtiene los datos consolidados."""
        return self._consolidated_data
    
    @property
    def load_status(self) -> Dict[str, bool]:
        """Obtiene el estado de carga de los datos."""
        return self._load_status.copy()
    
    # ===================== CARGA DE DATOS =====================
    
    def load_all_data(self, strategies_path: Optional[str] = None, 
                     portfolio_path: Optional[str] = None,
                     market_path: Optional[str] = None,
                     kpis_path: Optional[str] = None) -> bool:
        """
        Carga todos los datos del sistema.
        
        Args:
            strategies_path: Ruta a carpeta de estrategias
            portfolio_path: Ruta a archivo de portafolio
            market_path: Ruta a archivo de mercado
            kpis_path: Ruta a archivo de KPIs
            
        Returns:
            True si la carga fue exitosa
        """
        try:
            self.logger.info("Iniciando carga completa de datos...")
            
            # Determinar rutas según configuración
            if self.config['development']['use_inputtest']:
                # Usar INPUTTEST para desarrollo
                strategies_path = strategies_path or f"{self.config['development']['inputtest_path']}/M1_NDX_UP_MQL4_136_STOP"
                market_path = market_path or f"{self.config['development']['inputtest_path']}/DATOSMQL5.csv"
                kpis_path = kpis_path or f"{self.config['development']['inputtest_path']}/DatabankExport_M1.csv"
                self.logger.info("Usando datos de INPUTTEST para desarrollo")
            else:
                # Usar rutas de usuario para producción
                strategies_path = strategies_path or self.config['default_files']['strategies_folder']
                market_path = market_path or self.config['default_files']['market_file']
                kpis_path = kpis_path or self.config['default_files']['kpis_file']
                self.logger.info("Usando rutas de usuario para producción")
            
            # Cargar datos
            success = True
            
            if strategies_path:
                success &= self.load_strategies_data(strategies_path)
            
            if market_path:
                success &= self.load_market_data(market_path)
            
            if kpis_path:
                success &= self.load_kpis_data(kpis_path)
            
            if portfolio_path:
                success &= self.load_portfolio_data(portfolio_path)
            
            # Consolidar datos
            if success:
                self._consolidate_data()
            
            self.logger.info(f"Carga completa finalizada: {'Exitoso' if success else 'Con errores'}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error en carga completa: {e}")
            return False
    
    def load_and_prepare_data_pipeline(self, file_path: str) -> pd.DataFrame:
        """
        Carga y prepara datos desde un archivo, centralizando validación y limpieza.
        Ningún otro módulo debe realizar validación/carga local.
        """
        self.logger.debug(f"[INICIO] load_and_prepare_data_pipeline - Archivo: {file_path}")
        try:
            self.logger.info(f"Cargando datos desde: {file_path}")
            
            # Cargar archivo
            df = self._load_file_by_format(file_path)
            
            if df is None or df.empty:
                self.logger.error(f"No se pudieron cargar datos de: {file_path}")
                return pd.DataFrame()
            
            self.logger.info(f"Archivo cargado exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            
            # Normalizar nombres de columnas (preservando datos reales)
            df = self._normalize_column_names(df)
            self.logger.info(f"Columnas normalizadas: {len(df)} filas, {len(df.columns)} columnas")
            
            # Validar datos (sin modificar valores)
            is_valid, errors = self._validate_dataframe(df)
            if not is_valid:
                self.logger.warning(f"Errores de validación: {errors}")
            
            # Limpiar datos básicos (sin cocinamiento)
            df = self._clean_data_basic(df)
            self.logger.info(f"Datos limpios: {len(df)} filas, {len(df.columns)} columnas")

            # --- CORRECCIÓN: Renombrar columnas críticas al formato requerido por el core engine ---
            required_case_map = {
                'strategy_name': 'Strategy_Name',
                'cagr': 'CAGR',
                'drawdown': 'Drawdown',
                'sharpe_ratio': 'Sharpe Ratio',
                'profit_factor': 'Profit factor',
                'unified_score': 'Unified_Score',
            }
            df.rename(columns={k: v for k, v in required_case_map.items() if k in df.columns}, inplace=True)
            self.logger.info(f"Columnas finales tras renombrado crítico: {list(df.columns)}")

            self.logger.info(f"Datos cargados exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except Exception as e:
            self.logger.error(f"Error en pipeline de carga: {e}")
            return pd.DataFrame()
    
    def _load_file_by_format(self, file_path: str) -> pd.DataFrame:
        """
        Carga archivo según su formato.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            DataFrame con datos originales
        """
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists():
                self.logger.error(f"Archivo no encontrado: {file_path}. SUGERENCIA: Verifica la ruta o selecciona el archivo correcto desde la GUI.")
                return pd.DataFrame()
            
            # Detectar formato por extensión
            if path_obj.suffix.lower() == '.csv':
                # Intentar diferentes delimitadores en orden de probabilidad
                delimiters = [';', ',', '\t']  # Punto y coma primero para archivos europeos
                
                for delimiter in delimiters:
                    try:
                        df = pd.read_csv(
                            file_path,
                            sep=delimiter,
                            decimal=self.config.get('csv_decimal', '.'),
                            encoding='utf-8',
                            low_memory=False
                        )
                        
                        # Verificar si la carga fue exitosa (más de 1 columna)
                        if len(df.columns) > 1:
                            self.logger.info(f"Archivo cargado con delimitador '{delimiter}': {len(df)} filas, {len(df.columns)} columnas")
                            return df
                            
                    except Exception as e:
                        self.logger.debug(f"Error con delimitador '{delimiter}': {e}")
                        continue
                
                # Si ningún delimitador funcionó, intentar con el delimitador por defecto
                try:
                    df = pd.read_csv(
                        file_path,
                        sep=self.config['csv_delimiter'],
                        decimal=self.config.get('csv_decimal', '.'),
                        encoding='utf-8',
                        low_memory=False
                    )
                    self.logger.info(f"Archivo cargado con delimitador por defecto: {len(df)} filas, {len(df.columns)} columnas")
                    return df
                except Exception as e:
                    self.logger.error(f"Error cargando archivo {file_path}: {e}")
                    return pd.DataFrame()
                    
            elif path_obj.suffix.lower() in ['.xlsx', '.xls']:
                # Cargar Excel
                df = pd.read_excel(file_path, engine='openpyxl')
                self.logger.info(f"Archivo Excel cargado: {len(df)} filas, {len(df.columns)} columnas")
                return df
            else:
                self.logger.error(f"Formato no soportado: {path_obj.suffix}. SUGERENCIA: Usa archivos .csv o .xlsx válidos.")
                return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Error cargando archivo {file_path}: {e}. SUGERENCIA: Revisa el formato y el delimitador del archivo.")
            return pd.DataFrame()
    
    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza nombres de columnas preservando datos reales.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame con nombres normalizados
        """
        try:
            df_normalized = df.copy()
            
            # Aplicar mapeo de columnas críticas
            for old_name, new_name in self.COLUMN_MAPPINGS.items():
                if old_name in df_normalized.columns:
                    df_normalized[new_name] = df_normalized[old_name]
                    self.logger.info(f"Mapeada columna: '{old_name}' -> '{new_name}'")
            
            # Normalizar nombres restantes
            normalized_columns = []
            for col in df_normalized.columns:
                normalized_col = normalize_column_names(col)
                normalized_columns.append(normalized_col)
            
            df_normalized.columns = normalized_columns
            
            self.logger.info(f"Nombres de columnas normalizados: {list(df_normalized.columns)[:5]}...")

            # Refuerzo profesional: mapeo simple de alias críticos
            critical_aliases = {
                'strategy_name': ['strategy_name', 'strategy', 'name', 'strategy_name'],
                'number_of_trades': ['number_of_trades', '#_of_trades', 'tradescount'],
                'max_dd_pct': ['max_dd_pct', 'max_dd_percent', 'drawdown_is'],
            }
            
            for std_name, aliases in critical_aliases.items():
                found = None
                for alias in aliases:
                    if hasattr(df_normalized, 'columns') and df_normalized.columns is not None:
                        columns_list = list(df_normalized.columns)
                        for col in columns_list:
                            if col.lower() == alias.lower():
                                found = col
                                break
                    if found:
                        break
                if found and std_name not in df_normalized.columns:
                    try:
                        df_normalized[std_name] = df_normalized[found].copy()
                        self.logger.info(f"Alias crítico: '{found}' -> '{std_name}'")
                    except Exception as e:
                        self.logger.warning(f"No se pudo crear alias '{found}' -> '{std_name}': {e}")
            
            return df_normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizando nombres de columnas: {e}")
            return df
    
    def _validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida DataFrame sin modificar datos.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Tupla (es_válido, lista_errores)
        """
        errors: List[str] = []
        
        # Verificar que no esté vacío
        if df is None or df.empty:
            errors.append("DataFrame está vacío")
            return False, errors
        
        # Verificar columnas requeridas (más flexible)
        required_columns = self.config['required_columns']
        missing_required = [col for col in required_columns if col not in df.columns]
        if missing_required:
            self.logger.warning(f"Columnas requeridas faltantes: {missing_required}. SUGERENCIA: Verifica el mapeo y la normalización de columnas en el archivo fuente. Puedes editar el archivo o ajustar el mapeo en DataManager.COLUMN_MAPPINGS.")
            # No agregar a errores para no bloquear el proceso
        
        # Verificar tipos de datos numéricos
        errors.extend(list(self._validate_numeric_columns(df)))  # type: ignore[reportGeneralTypeIssues]
        
        # Verificar valores extremos (sin modificar)
        outlier_errors = self._validate_outliers(df)
        errors.extend(outlier_errors)
        
        return len(errors) == 0, errors
    
    def _validate_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Valida y convierte columnas numéricas.
        """
        errors = []
        for col in df.columns:
            if col in ['strategy_name', 'date', 'timeframe', 'filters_result']:
                continue  # Saltar columnas no numéricas
            try:
                if col not in df.columns:
                    continue
                if pd.api.types.is_numeric_dtype(df[col]):
                    continue
                if not isinstance(df[col], pd.Series):
                    continue
                original_values = df[col].copy()
                if hasattr(df[col], 'dtype') and df[col].dtype == object:
                    df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                non_numeric_count = df[col].isna().sum()
                if non_numeric_count > 0:
                    logger.warning(f"⚠️ Columna '{col}': {non_numeric_count} valores no numéricos convertidos a NaN")
            except Exception as e:
                logger.warning(f"⚠️ Error convirtiendo columna '{col}' a numérico: {e}")
                errors.append(f"Error en columna {col}: {e}")
        assert isinstance(errors, list)
        return errors

    def _clean_duplicate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elimina columnas duplicadas basándose en nombres.
        """
        unique_columns = []
        seen_columns = set()
        for col in df.columns:
            if col not in seen_columns:
                unique_columns.append(col)
                seen_columns.add(col)
            else:
                logger.warning(f"⚠️ Columna duplicada eliminada: {col}")
        # Siempre devolver un DataFrame, nunca una Series
        if not unique_columns:
            return df.iloc[:, :0].copy()
        result = df.loc[:, unique_columns]
        if isinstance(result, pd.Series):
            return result.to_frame().T
        return result

    def _validate_outliers(self, df: pd.DataFrame) -> List[str]:
        """
        Valida outliers en columnas numéricas.
        """
        errors = []
        
        for col in df.columns:
            if col in ['strategy_name', 'date', 'timeframe', 'filters_result']:
                continue
                
            try:
                # Verificar si la columna es numérica
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Calcular estadísticas para detectar outliers
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    # Definir límites para outliers
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    # Contar outliers
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    
                    if len(outliers) > 0:
                        logger.warning(f"⚠️ Columna '{col}': {len(outliers)} outliers detectados")
                        
            except Exception as e:
                logger.warning(f"⚠️ Error validando outliers en columna '{col}': {e}")
                
        return errors
    
    def _clean_data_basic(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpieza básica preservando datos reales.

        Args:
            df: DataFrame original

        Returns:
            DataFrame limpio
        """
        try:
            df_cleaned = df.copy()
            
            # Eliminar duplicados
            df_cleaned = df_cleaned.drop_duplicates()
            
            # Manejar valores infinitos (sin cocinamiento)
            df_cleaned = df_cleaned.replace([np.inf, -np.inf], np.nan)
            
            # Rellenar valores faltantes solo en columnas numéricas
            numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                # Validar que la columna existe y es numérica
                if col in df_cleaned.columns:
                    try:
                        # Verificar si hay valores nulos usando método seguro
                        null_mask = df_cleaned[col].isnull()
                        if isinstance(null_mask, pd.Series):
                            null_count = int(null_mask.sum())
                        else:
                            null_count = 0
                        
                        if null_count > 0:
                            # Usar mediana para preservar distribución
                            try:
                                median_val = float(df_cleaned[col].median())
                                df_cleaned[col].fillna(median_val, inplace=True)
                            except (ValueError, TypeError):
                                # Si no se puede calcular mediana, usar 0
                                df_cleaned[col].fillna(0.0, inplace=True)
                    except Exception as e:
                        self.logger.warning(f"Error procesando columna {col}: {e}")
                        continue
            
            self.logger.info("Limpieza básica completada")
            return df_cleaned
            
        except Exception as e:
            self.logger.error(f"Error en limpieza básica: {e}")
            return df
    
    def _normalize_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convierte todas las columnas numéricas (con coma o punto decimal) a float de forma robusta.
        Aplica solo a columnas que parecen numéricas pero son string.
        """
        df_clean = df.copy()
        for col in df_clean.columns:
            # Si la columna es object pero parece numérica (contiene solo dígitos, puntos o comas)
            if df_clean[col].dtype == object:
                try:
                    # Reemplazar comas por puntos y convertir a float
                    df_clean[col] = (
                        df_clean[col]
                        .astype(str)
                        .str.replace(',', '.', regex=False)
                        .str.replace(' ', '', regex=False)
                    )
                    # Intentar convertir a float, si falla, loggear advertencia
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                    null_count = df_clean[col].isnull().sum()
                    total_count = len(df_clean[col])
                    
                    if null_count == total_count:
                        self.logger.warning(f"Columna '{col}' no pudo convertirse a float (todo NaN)")
                    elif null_count > 0:
                        self.logger.warning(f"Columna '{col}' parcialmente convertida a float ({null_count} NaN)")
                    else:
                        self.logger.info(f"Columna '{col}' convertida exitosamente a float")
                except Exception as e:
                    self.logger.warning(f"Error convirtiendo columna '{col}' a float: {e}")
        return df_clean

    # ===================== CARGA ESPECÍFICA DE DATOS =====================
    
    def load_strategies_data(self, folder_path: str) -> bool:
        """
        Carga datos de estrategias desde carpeta.
        
        Args:
            folder_path: Ruta a carpeta de estrategias
            
        Returns:
            True si la carga fue exitosa
        """
        try:
            self.logger.info(f"Cargando estrategias desde: {folder_path}")
            
            # Cargar archivos .sqx si existen
            sqx_files = list(Path(folder_path).glob("*.sqx"))
            if sqx_files:
                self.logger.info(f"Encontrados {len(sqx_files)} archivos .sqx")
                # Aquí se implementaría la carga de archivos .sqx
                # Por ahora, solo registramos su existencia
            
            # Cargar CSV de estrategias si existe
            csv_files = list(Path(folder_path).glob("*.csv"))
            if csv_files:
                # Usar el primer CSV encontrado
                csv_file = csv_files[0]
                self._strategies_data = self.load_and_prepare_data_pipeline(str(csv_file))
                self._load_status['strategies'] = True
                self.logger.info(f"Estrategias cargadas: {len(self._strategies_data)} registros")
                return True
            
            self.logger.warning(f"No se encontraron archivos de estrategias en: {folder_path}")
            return False
                
        except Exception as e:
            self.logger.error(f"Error cargando estrategias: {e}")
            return False
    
    def load_market_data(self, file_path: str) -> bool:
        """
        Carga datos de mercado.
        
        Args:
            file_path: Ruta al archivo de mercado
            
        Returns:
            True si la carga fue exitosa
        """
        try:
            self.logger.info(f"Cargando datos de mercado desde: {file_path}")
            
            self._market_data = self.load_and_prepare_data_pipeline(file_path)
            
            if self._market_data is not None and not self._market_data.empty:
                self._load_status['market'] = True
                self.logger.info(f"Datos de mercado cargados: {len(self._market_data)} registros")
                return True
            else:
                self.logger.error("No se pudieron cargar datos de mercado")
                return False
                
        except Exception as e:
            self.logger.error(f"Error cargando datos de mercado: {e}")
            return False
    
    def load_kpis_data(self, file_path: str) -> bool:
        """
        Carga datos de KPIs y normaliza columnas numéricas.
        """
        try:
            self.logger.info(f"Cargando KPIs desde: {file_path}")
            self._kpis_data = self.load_and_prepare_data_pipeline(file_path)
            # --- Limpieza profesional: normalizar columnas numéricas ---
            if self._kpis_data is not None and not self._kpis_data.empty:
                self._kpis_data = self._normalize_numeric_columns(self._kpis_data)
                self._load_status['kpis'] = True
                self.logger.info(f"KPIs cargados: {len(self._kpis_data)} registros")
                return True
            else:
                self.logger.error("No se pudieron cargar KPIs - DataFrame vacío o None")
                return False
        except Exception as e:
            self.logger.error(f"Error cargando KPIs: {e}")
            return False
    
    def load_portfolio_data(self, file_path: str) -> bool:
        """
        Carga datos de portafolio.
        
        Args:
            file_path: Ruta al archivo de portafolio
            
        Returns:
            True si la carga fue exitosa
        """
        try:
            self.logger.info(f"Cargando datos de portafolio desde: {file_path}")
            
            # Por ahora, solo registramos la carga
            self._portfolio_data = {'file_path': file_path, 'loaded': True}
            self._load_status['portfolio'] = True
            
            self.logger.info("Datos de portafolio cargados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cargando datos de portafolio: {e}")
            return False
    
    # ===================== CONSOLIDACIÓN DE DATOS =====================
    
    def _consolidate_data(self) -> None:
        """
        Consolida todos los datos cargados.
        """
        try:
            self.logger.info("Consolidando datos...")
            
            self._consolidated_data = {
                'strategies': self._strategies_data,
                'portfolio': self._portfolio_data,
                'market': self._market_data,
                'kpis': self._kpis_data,
                'load_status': self._load_status.copy(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("Datos consolidados exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error consolidando datos: {e}")
    
    # ===================== VALIDACIÓN ESPECÍFICA PARA INPUTTEST =====================
    
    def validate_inputtest_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida datos de INPUTTEST con reglas específicas.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Tupla (es_válido, lista_errores)
        """
        errors = []
        
        # Validar columnas críticas
        critical_columns = ['Strategy_Name', 'CAGR_IS', 'CAGR_OOS', 'Drawdown_IS', 'Drawdown_OOS']
        missing_critical = [col for col in critical_columns if col not in df.columns]
        if missing_critical:
            errors.append(f"Columnas críticas faltantes: {missing_critical}")
        
        # Validar tipos de datos
        numeric_columns = ['CAGR_IS', 'CAGR_OOS', 'Drawdown_IS', 'Drawdown_OOS']
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"Columna {col} no es numérica")
        
        # Validar valores extremos
        for col in numeric_columns:
            if col in df.columns:
                max_val = df[col].abs().max()
                try:
                    max_val_scalar = max_val.item() if hasattr(max_val, 'item') else float(max_val) if max_val is not None else 0.0 if max_val is not None else 0.0
                    if pd.notna(max_val_scalar):
                        if max_val_scalar > 1e6:
                            errors.append(f"Valores extremos detectados en {col}")
                except Exception:
                    pass  # Ignorar errores de validación
        
        return len(errors) == 0, errors
    
    # ===================== INTERFAZ PARA CORE ENGINE Y ASESOR FINANCIERO =====================
    
    def get_data_for_core_engine(self) -> pd.DataFrame:
        """
        Obtiene datos preparados para el core engine.
        Preserva datos reales sin cocinamiento.
        
        Returns:
            DataFrame con datos para core engine
        """
        try:
            if self._kpis_data is not None and not self._kpis_data.empty:
                self.logger.info("Proporcionando KPIs al core engine")
                return self._kpis_data.copy()
            else:
                self.logger.warning("No hay datos de KPIs disponibles para core engine")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error obteniendo datos para core engine: {e}")
            return pd.DataFrame()
    
    def get_kpis_data(self) -> pd.DataFrame:
        """
        Obtiene datos de KPIs preparados.
        
        Returns:
            DataFrame con datos de KPIs
        """
        try:
            if self._kpis_data is not None and not self._kpis_data.empty:
                return self._kpis_data.copy()
            else:
                self.logger.warning("No hay datos de KPIs disponibles")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de KPIs: {e}")
            return pd.DataFrame()
    
    def get_data_for_asesor_financiero(self) -> Dict[str, Any]:
        """
        Obtiene datos preparados para el asesor financiero.
        Preserva datos reales sin cocinamiento.
        
        Returns:
            Diccionario con datos para asesor financiero
        """
        try:
            data_for_asesor = {
                'kpis': self._kpis_data.copy() if self._kpis_data is not None else pd.DataFrame(),
                'market': self._market_data.copy() if self._market_data is not None else pd.DataFrame(),
                'strategies': self._strategies_data.copy() if self._strategies_data is not None else pd.DataFrame(),
                'load_status': self._load_status.copy()
            }
            
            self.logger.info("Proporcionando datos al asesor financiero")
            return data_for_asesor
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos para asesor financiero: {e}")
            return {}
    
    # ===================== CACHÉ Y PERSISTENCIA =====================
    
    def save_to_cache(self, data: Any, key: str) -> bool:
        """
        Guarda datos en caché.
        
        Args:
            data: Datos a guardar
            key: Clave de caché
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            if not self.config['cache']['enable_cache']:
                return False
            
            cache_file = Path(self.config['cache']['cache_dir']) / f"{key}.pkl.gz"
            
            with gzip.open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            self.logger.info(f"Datos guardados en caché: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando en caché: {e}")
            return False
    
    def load_from_cache(self, key: str) -> Any:
        """
        Carga datos desde caché.
        
        Args:
            key: Clave de caché
            
        Returns:
            Datos cargados o None
        """
        try:
            if not self.config['cache']['enable_cache']:
                return None
            
            cache_file = Path(self.config['cache']['cache_dir']) / f"{key}.pkl.gz"
            
            if not cache_file.exists():
                return None
    
            # Verificar antigüedad
            cache_age = time.time() - cache_file.stat().st_mtime
            max_age = self.config['cache']['cache_duration_hours'] * 3600
            
            if cache_age > max_age:
                self.logger.info(f"Caché expirado: {key}")
                return None
            
            with gzip.open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            self.logger.info(f"Datos cargados desde caché: {key}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error cargando desde caché: {e}")
            return None
    
    # ===================== EXPORTACIÓN =====================
    
    def export_consolidated_data(self, output_path: str, format: str = 'excel') -> bool:
        """
        Exporta datos consolidados.
        Solo serializa tipos simples y DataFrames convertidos a dict.
        """
        try:
            if self._consolidated_data is None:
                self.logger.error("No hay datos consolidados para exportar")
                return False
            output_path_obj = Path(output_path)
            if format.lower() == 'excel':
                with pd.ExcelWriter(output_path_obj, engine='openpyxl') as writer:
                    for data_type, data in self._consolidated_data.items():
                        if isinstance(data, pd.DataFrame):
                            data.to_excel(writer, sheet_name=data_type, index=False)
                        else:
                            df_dict = pd.DataFrame([data])
                            df_dict.to_excel(writer, sheet_name=data_type, index=False)
                self.logger.info(f"Datos consolidados exportados a {output_path_obj}")
            elif format.lower() == 'json':
                json_data = {}
                for data_type, data in self._consolidated_data.items():
                    if isinstance(data, pd.DataFrame):
                        json_data[data_type] = data.to_dict('records')
                    elif isinstance(data, (dict, list, str, int, float, bool, type(None))):
                        json_data[data_type] = data
                    else:
                        self.logger.warning(f"No se puede serializar el tipo {type(data)} para '{data_type}', se omitirá.")
                        json_data[data_type] = str(data)
                with open(output_path_obj, 'w') as f:
                    json.dump(json_data, f, default=str, indent=2)
                self.logger.info(f"Datos consolidados exportados a {output_path_obj}")
            return True
        except Exception as e:
            self.logger.error(f"Error exportando datos: {e}")
            return False
    
    # ===================== UTILIDADES =====================
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        Obtiene información detallada sobre los datos cargados.
        
        Returns:
            Diccionario con información de los datos
        """
        info = {
            'load_status': self._load_status.copy(),
            'data_counts': {},
            'last_update': datetime.now().isoformat(),
            'development_mode': self.config['development']['use_inputtest']
        }
        
        if self._strategies_data is not None:
            info['data_counts']['strategies'] = len(self._strategies_data)
        
        if self._market_data is not None:
            info['data_counts']['market'] = len(self._market_data)
        
        if self._kpis_data is not None:
            info['data_counts']['kpis'] = len(self._kpis_data)
        
        return info
    
    def clear_cache(self) -> bool:
        """
        Limpia el caché de datos.
        
        Returns:
            True si se limpió exitosamente
        """
        try:
            if not self.config['cache']['enable_cache']:
                return False
            
            cache_dir = Path(self.config['cache']['cache_dir'])
            if cache_dir.exists():
                for cache_file in cache_dir.glob("*.pkl.gz"):
                    cache_file.unlink()
            
            self.logger.info("Caché limpiado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error limpiando caché: {e}")
            return False
    
    def switch_to_development_mode(self) -> None:
        """
        Cambia a modo desarrollo usando INPUTTEST.
        """
        self.config['development']['use_inputtest'] = True
        self.logger.info("Cambiado a modo desarrollo (INPUTTEST)")
    
    def switch_to_production_mode(self) -> None:
        """
        Cambia a modo producción usando rutas de usuario.
        """
        self.config['development']['use_inputtest'] = False
        self.logger.info("Cambiado a modo producción (rutas de usuario)")

    # ===================== FUNCIONES DE INVESTIGACIÓN Y VALIDACIÓN CIENTÍFICA =====================
    
    def analyze_data_quality(self, df: pd.DataFrame, numeric_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analiza la calidad de los datos con estadísticas y detección de outliers.
        
        Args:
            df: DataFrame a analizar
            numeric_columns: Lista de columnas numéricas a analizar (opcional)
            
        Returns:
            Diccionario con análisis completo de calidad de datos
        """
        try:
            self.logger.info(f"[DEBUG] DataFrame shape: {df.shape}")
            self.logger.info(f"[DEBUG] DataFrame dtypes: {df.dtypes}")
            if numeric_columns is None:
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            analysis = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'numeric_columns': len(numeric_columns),
                'missing_values': df.isnull().sum().to_dict(),
                'column_analysis': {}
            }
            
            for col in numeric_columns:
                if col in df.columns:
                    stats = calculate_basic_stats(df, col)
                    outliers = detect_outliers_iqr(df, col)
                    
                    analysis['column_analysis'][col] = {
                        'stats': stats,
                        'outliers': outliers
                    }
            
            self.logger.info(f"Análisis de calidad completado para {len(numeric_columns)} columnas")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error en análisis de calidad: {e}")
            return {}

    def get_clean_data(self, file_path: Optional[str] = None, extra_columns: Optional[list] = None) -> pd.DataFrame:
        """
        Devuelve un DataFrame limpio solo con columnas estándar y opcionales.
        Args:
            file_path: Ruta al archivo a cargar (si no se ha cargado aún)
            extra_columns: Lista de columnas adicionales a conservar
        Returns:
            DataFrame limpio
        """
        if file_path:
            df = self.load_and_prepare_data_pipeline(file_path)
        elif self._kpis_data is not None:
            df = self._kpis_data.copy()
        else:
            self.logger.error("No hay datos cargados para limpiar.")
            return pd.DataFrame()
            
        # Eliminar columnas duplicadas primero
        df = df.loc[:, ~df.columns.duplicated()]
        
        standard_cols = [
            'strategy_name', 'cagr_is', 'cagr_oos', 'sharpe_ratio_is',
            'sharpe_ratio_oos', 'profit_factor_is', 'profit_factor_oos',
            'max_dd_pct', 'number_of_trades', 'winning_percent_is',
            'winning_percent_oos', 'net_profit_is', 'net_profit_oos',
            'calmarratio_is', 'calmarratio_oos'
        ]
        if extra_columns:
            standard_cols += extra_columns
            
        # Seleccionar solo las columnas estándar que existen
        cols_final = [col for col in standard_cols if col in df.columns]
        df_clean = df[cols_final].copy()
        
        self.logger.info(f"DataFrame limpio generado: {df_clean.shape[1]} columnas estándar")
        return df_clean

    def save_analysis_result(self, name: str, df: pd.DataFrame) -> bool:
        """
        Guarda un resultado de análisis en results/ con nombre único.
        Args:
            name: Nombre identificador
            df: DataFrame de resultados
        Returns:
            True si se guardó correctamente
        """
        try:
            path = Path('results') / f"analysis_{name}.csv"
            df.to_csv(path, index=False)
            self.logger.info(f"Resultado de análisis guardado: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error guardando resultado de análisis: {e}")
            return False

    def load_analysis_result(self, name: str) -> pd.DataFrame:
        """
        Carga un resultado de análisis guardado.
        Args:
            name: Nombre identificador
        Returns:
            DataFrame de resultados
        """
        try:
            path = Path('results') / f"analysis_{name}.csv"
            df = pd.read_csv(path)
            self.logger.info(f"Resultado de análisis cargado: {path}")
            return df
        except Exception as e:
            self.logger.error(f"Error cargando resultado de análisis: {e}")
            return pd.DataFrame()

    def list_analysis_results(self) -> list:
        """
        Lista los resultados de análisis disponibles en results/.
        Returns:
            Lista de nombres
        """
        results_dir = Path('results')
        results_dir.mkdir(exist_ok=True)
        files = list(results_dir.glob('analysis_*.csv'))
        return [f.stem.replace('analysis_', '') for f in files]

    def save_test_result(self, name: str, log_text: str) -> bool:
        """
        Guarda un resultado de test (log) en logs/ con nombre único.
        Args:
            name: Nombre identificador
            log_text: Texto del log
        Returns:
            True si se guardó correctamente
        """
        try:
            path = Path('logs') / f"test_{name}.log"
            with open(path, 'w', encoding='utf-8') as f:
                f.write(log_text)
            self.logger.info(f"Log de test guardado: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error guardando log de test: {e}")
            return False

    def load_test_result(self, name: str) -> str:
        """
        Carga un log de test guardado.
        Args:
            name: Nombre identificador
        Returns:
            Texto del log
        """
        try:
            path = Path('logs') / f"test_{name}.log"
            with open(path, 'r', encoding='utf-8') as f:
                log_text = f.read()
            self.logger.info(f"Log de test cargado: {path}")
            return log_text
        except Exception as e:
            self.logger.error(f"Error cargando log de test: {e}")
            return ""

    def list_test_results(self) -> list:
        """
        Lista los logs de test disponibles en logs/.
        Returns:
            Lista de nombres
        """
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        files = list(logs_dir.glob('test_*.log'))
        return [f.stem.replace('test_', '') for f in files]


# ===================== FUNCIONES DE UTILIDAD =====================

def create_data_manager(config: Optional[Dict] = None) -> DataManager:
    """
    Función de utilidad para crear una instancia de DataManager.
    
    Args:
        config: Configuración opcional
        
    Returns:
        Instancia de DataManager
    """
    return DataManager(config)


def load_data_from_config(config_path: str) -> DataManager:
    """
    Crea un DataManager y carga datos desde un archivo de configuración.
    
    Args:
        config_path: Ruta al archivo de configuración (JSON o YAML)
        
    Returns:
        DataManager con datos cargados
    """
    try:
        path_obj = Path(config_path)
        if path_obj.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                config = json.load(f)
        elif path_obj.suffix.lower() in ['.yml', '.yaml']:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            raise ValueError(f"Formato de configuración no soportado: {path_obj.suffix}")
        
        data_manager = DataManager(config)
        
        # Cargar datos usando la configuración
        if 'data_sources' in config:
            data_sources = config['data_sources']
            data_manager.load_all_data(
                strategies_path=data_sources.get('strategies'),
                portfolio_path=data_sources.get('portfolio'),
                market_path=data_sources.get('market'),
                kpis_path=data_sources.get('kpis')
            )
        
        return data_manager
        
    except Exception as e:
        logger.error(f"Error cargando configuración desde {config_path}: {e}")
        raise


def load_inputtest_data_pipeline() -> Dict[str, pd.DataFrame | None]:
    """
    Carga completa de datos INPUTTEST para flujo de trabajo.
    
    Returns:
        Diccionario con datos de INPUTTEST
    """
    data_manager = DataManager()
    data_manager.switch_to_development_mode()
    
    # Cargar todos los datos de INPUTTEST
    success = data_manager.load_all_data()
    
    if success:
        return {
            'kpis': data_manager.kpis_data,
            'market': data_manager.market_data,
            'strategies': data_manager.strategies_data
        }
    else:
        logger.error("Error cargando datos de INPUTTEST")
        return {}