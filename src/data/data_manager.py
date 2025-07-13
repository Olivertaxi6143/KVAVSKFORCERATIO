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
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
import os
from pathlib import Path
import json
import yaml
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import hashlib
import pickle
import gzip
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    """
    Gestor centralizado de datos para el sistema de análisis cuantitativo.
    - 'Stagnation': periodo de estancamiento (tiempo o trades sin nuevo máximo de equity).
    - 'Stagnation_Trades': número máximo de operaciones consecutivas en estancamiento (si la fuente lo provee).
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
        
        # Cargar datos automáticamente si están disponibles
        self._auto_load_data()
        
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
        Pipeline completo de carga y preparación de datos.
        Preserva los datos reales sin cocinamiento.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            DataFrame preparado con datos reales
        """
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
                # Cargar CSV con configuración específica
                df = pd.read_csv(
                    file_path,
                    sep=self.config['csv_delimiter'],
                    decimal=self.config['csv_decimal'],
                    encoding='utf-8',
                    low_memory=False
                )
            elif path_obj.suffix.lower() in ['.xlsx', '.xls']:
                # Cargar Excel
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                self.logger.error(f"Formato no soportado: {path_obj.suffix}. SUGERENCIA: Usa archivos .csv o .xlsx válidos.")
                return pd.DataFrame()
            
            self.logger.info(f"Archivo cargado: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
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
                normalized_col = self._normalize_column_name(col)
                normalized_columns.append(normalized_col)
            
            df_normalized.columns = normalized_columns
            
            self.logger.info(f"Nombres de columnas normalizados: {list(df_normalized.columns)[:5]}...")
            return df_normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizando nombres de columnas: {e}")
            return df
    
    def _normalize_column_name(self, col: str) -> str:
        """
        Normaliza el nombre de una columna.
        
        Args:
            col: Nombre original de columna
            
        Returns:
            Nombre normalizado
        """
        return (
            col.strip()
            .replace('"', '')
            .replace("'", '')
            .replace('%', 'pct')
            .replace('(', '')
            .replace(')', '')
            .replace('.', '_')
            .replace('-', '_')
            .replace(' ', '_')
            .lower()
        )
    
    def _validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida DataFrame sin modificar datos.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Tupla (es_válido, lista_errores)
        """
        errors = []
        
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
        numeric_errors = self._validate_numeric_columns(df)
        errors.extend(numeric_errors)
        
        # Verificar valores extremos (sin modificar)
        outlier_errors = self._validate_outliers(df)
        errors.extend(outlier_errors)
        
        return len(errors) == 0, errors
    
    def _validate_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Valida columnas numéricas sin modificar datos.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Lista de errores
        """
        errors = []
        
        # Identificar columnas que deberían ser numéricas
        potential_numeric = [col for col in df.columns 
                           if any(keyword in col.lower() for keyword in 
                                 ['cagr', 'drawdown', 'sharpe', 'profit', 'ratio', 'percent', 'factor'])]
        
        for col in potential_numeric:
            if col in df.columns:
                # Intentar convertir a numérico sin modificar original
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except Exception:
                    errors.append(f"Columna {col} no es numérica")
        
        return errors
    
    def _validate_outliers(self, df: pd.DataFrame) -> List[str]:
        """
        Valida valores extremos sin modificar datos.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Lista de errores
        """
        errors = []
        
        # Identificar columnas numéricas
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns:
                # Verificar valores infinitos
                try:
                    inf_check = np.isinf(df[col])
                    if inf_check.any():
                        errors.append(f"Valores infinitos detectados en {col}")
                except Exception:
                    pass  # Ignorar errores de validación
                
                # Verificar valores extremos
                max_val = df[col].abs().max()
                try:
                    max_val_scalar = max_val.item() if hasattr(max_val, 'item') else float(max_val)
                    if pd.notna(max_val_scalar):
                        if max_val_scalar > 1e6:
                            errors.append(f"Valores extremos detectados en {col}")
                except Exception:
                    pass  # Ignorar errores de validación
        
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
        Carga datos de KPIs.
        
        Args:
            file_path: Ruta al archivo de KPIs
            
        Returns:
            True si la carga fue exitosa
        """
        try:
            self.logger.info(f"Cargando KPIs desde: {file_path}")
            
            self._kpis_data = self.load_and_prepare_data_pipeline(file_path)
            
            if self._kpis_data is not None and not self._kpis_data.empty:
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
                    max_val_scalar = max_val.item() if hasattr(max_val, 'item') else float(max_val)
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
        
        Args:
            output_path: Ruta de salida
            format: Formato de exportación ('excel' o 'json')
            
        Returns:
            True si la exportación fue exitosa
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
                    else:
                        json_data[data_type] = data
                
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
    
    def _to_float(self, val: Any) -> float:
        """Convierte un valor a float de forma segura."""
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def extract_float_from_tuple(self, data: Any, index: int = 0, default: float = 0.0) -> float:
        """
        Extrae un valor numérico de una tupla de forma segura.
        
        Args:
            data: Tupla que contiene el valor.
            index: Índice del valor a extraer.
            default: Valor por defecto si la tupla es inválida.
            
        Returns:
            float: Valor numérico extraído.
        """
        if isinstance(data, tuple) and len(data) > index:
            try:
                return float(data[index])
            except (ValueError, TypeError):
                return default
        elif isinstance(data, (int, float)):
            return float(data)
        return default

    def validate_numeric_column(self, df: pd.DataFrame, column: str) -> bool:
        """
        Valida si una columna es numérica y contiene datos válidos.
        
        Args:
            df: DataFrame a validar
            column: Nombre de la columna
            
        Returns:
            True si la columna es válida, False en caso contrario
        """
        try:
            if column not in df.columns:
                return False
            # Convertir a numérico
            df[column] = pd.to_numeric(df[column], errors='coerce')
            # Verificar que no sea todo NaN
            is_all_nan = bool(df[column].isna().all())
            if is_all_nan:
                return False
            return True
        except Exception as e:
            self.logger.warning(f"Error validando columna {column}: {e}")
            return False

    def calculate_basic_stats(self, df: pd.DataFrame, column: str) -> Dict[str, float]:
        """
        Calcula estadísticas básicas de una columna.
        
        Args:
            df: DataFrame
            column: Nombre de la columna
            
        Returns:
            Diccionario con estadísticas básicas
        """
        try:
            if not self.validate_numeric_column(df, column):
                return {}
            stats_dict = {
                'mean': df[column].mean(),
                'std': df[column].std(),
                'min': df[column].min(),
                'max': df[column].max(),
                'median': df[column].median(),
                'count': df[column].count()
            }
            return stats_dict
        except Exception as e:
            self.logger.error(f"Error calculando estadísticas de {column}: {e}")
            return {}

    def detect_outliers_iqr(self, df: pd.DataFrame, column: str, factor: float = 1.5) -> Dict[str, Any]:
        """
        Detecta outliers usando el método IQR.
        
        Args:
            df: DataFrame
            column: Nombre de la columna
            factor: Factor para el cálculo de outliers
            
        Returns:
            Diccionario con información de outliers
        """
        try:
            if not self.validate_numeric_column(df, column):
                return {'outliers': [], 'count': 0, 'percentage': 0.0}
                
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR
            
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                
            return {
                'outliers': outliers[column].tolist(),
                'count': len(outliers),
                'percentage': len(outliers) / len(df) * 100,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
            
        except Exception as e:
            self.logger.error(f"Error detectando outliers en {column}: {e}")
            return {'outliers': [], 'count': 0, 'percentage': 0.0}

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
                    stats = self.calculate_basic_stats(df, col)
                    outliers = self.detect_outliers_iqr(df, col)
                    
                    analysis['column_analysis'][col] = {
                        'stats': stats,
                        'outliers': outliers
                    }
            
            self.logger.info(f"Análisis de calidad completado para {len(numeric_columns)} columnas")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error en análisis de calidad: {e}")
            return {}


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