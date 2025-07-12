"""
Procesamiento de datos para análisis de estrategias de trading.
Módulo simplificado con solo la clase DataManager esencial.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import os
import hashlib
import pickle
import gzip
import time

logger = logging.getLogger(__name__)

class DataValidator:
    """Validador de datos para verificar integridad y calidad."""
    
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
                elif bool(df[col].isna().sum() > len(df) * 0.5):  # Más del 50% NaN
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
    
    def validate_strategy_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida datos de estrategias específicamente."""
        errors = []
        
        # Verificar que no esté vacío
        if df.empty:
            errors.append("DataFrame de estrategias está vacío")
            return False, errors
        
        # Verificar columnas básicas de estrategias
        strategy_columns = ['Strategy_Name', 'Strategy', 'Net_Profit', 'Sharpe_Ratio']
        missing_strategy_cols = [col for col in strategy_columns if col not in df.columns]
        if missing_strategy_cols:
            errors.append(f"Columnas de estrategia faltantes: {missing_strategy_cols}")
        
        # Verificar tipos de datos numéricos solo si las columnas existen
        numeric_errors = []
        for col in self.required_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    numeric_errors.append(f"Columna {col} no es numérica")
                elif bool(df[col].isna().sum() > len(df) * 0.5):  # Más del 50% NaN
                    numeric_errors.append(f"Columna {col} tiene demasiados valores faltantes")
            else:
                # Si la columna no existe, no es un error crítico para estrategias
                pass
        
        errors.extend(numeric_errors)
        
        return len(errors) == 0, errors
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y prepara los datos."""
        df_cleaned = df.copy()
        
        # Eliminar duplicados
        df_cleaned = df_cleaned.drop_duplicates()
        
        # Manejar valores infinitos
        df_cleaned = df_cleaned.replace([np.inf, -np.inf], np.nan)
        
        # Rellenar valores faltantes numéricos con mediana
        numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if bool(df_cleaned[col].isnull().any()):
                median_val = df_cleaned[col].median()
                df_cleaned[col].fillna(median_val, inplace=True)
        
        # Rellenar valores faltantes categóricos con la moda o 'N/A'
        categorical_columns = df_cleaned.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if bool(df_cleaned[col].isnull().any()):
                mode_value = df_cleaned[col].mode()
                if not mode_value.empty:
                    df_cleaned[col] = df_cleaned[col].fillna(mode_value.iloc[0])
                else:
                    df_cleaned[col] = df_cleaned[col].fillna('N/A')
        
        return df_cleaned

class DataManager:
    """
    Gestor centralizado de datos para el sistema de análisis cuantitativo.
    
    Integra datos de múltiples fuentes:
    - Archivos CSV de StrategyQuant
    - Reportes PDF de portafolios
    - Datos de mercado (DATOSMQL5.csv)
    - KPIs históricos (DatabankExport_M1.csv)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el gestor de datos.
        
        Args:
            config: Configuración opcional del sistema
        """
        self.config = config or {}
        self.strategies_data = None
        self.portfolio_data = None
        self.market_data = None
        self.kpis_data = None
        self.logger = logging.getLogger(__name__)
        
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
            }
        }
        
        # Actualizar configuración
        self.config.update(self.default_config)
        
        self.logger.info("DataManager inicializado correctamente")
    
    def load_strategies_csv(self, file_path: str) -> pd.DataFrame:
        """
        Carga datos de estrategias desde archivo CSV.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            DataFrame con datos de estrategias
        """
        try:
            df = pd.read_csv(file_path, sep=self.config['csv_delimiter'], 
                           decimal=self.config['csv_decimal'])
            
            # Normalizar nombres de columnas
            df.columns = [col.strip().replace(' ', '_').upper() for col in df.columns]
            
            # Validar columnas requeridas
            missing_cols = [col for col in self.config['required_columns'] 
                          if col not in df.columns]
            if missing_cols:
                self.logger.warning(f"Columnas faltantes: {missing_cols}")
            
            self.strategies_data = df
            self.logger.info(f"Datos de estrategias cargados: {len(df)} filas")
            return df
            
        except Exception as e:
            self.logger.error(f"Error cargando estrategias: {e}")
            return pd.DataFrame()
    
    def load_portfolio_pdf(self, file_path: str) -> Dict:
        """
        Carga datos de portafolio desde archivo PDF.
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con datos del portafolio
        """
        try:
            # Por ahora retornamos un diccionario vacío
            # La implementación real dependería de la librería de PDF
            self.logger.info("Carga de PDFs no implementada aún")
            return {}
            
        except Exception as e:
            self.logger.error(f"Error cargando portafolio: {e}")
            return {}
    
    def load_market_data(self, file_path: str) -> pd.DataFrame:
        """
        Carga datos de mercado desde archivo CSV.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            DataFrame con datos de mercado
        """
        try:
            df = pd.read_csv(file_path, sep=self.config['csv_delimiter'], 
                           decimal=self.config['csv_decimal'])
            
            # Normalizar nombres de columnas
            df.columns = [col.strip().replace(' ', '_').upper() for col in df.columns]
            
            self.market_data = df
            self.logger.info(f"Datos de mercado cargados: {len(df)} filas")
            return df
            
        except Exception as e:
            self.logger.error(f"Error cargando mercado: {e}")
            return pd.DataFrame()
    
    def load_kpis_data(self, file_path: str) -> pd.DataFrame:
        """
        Carga datos de KPIs desde archivo CSV.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            DataFrame con datos de KPIs
        """
        try:
            df = pd.read_csv(file_path, sep=self.config['csv_delimiter'], 
                           decimal=self.config['csv_decimal'])
            
            # Normalizar nombres de columnas
            df.columns = [col.strip().replace(' ', '_').upper() for col in df.columns]
            
            self.kpis_data = df
            self.logger.info(f"Datos de KPIs cargados: {len(df)} filas")
            return df
            
        except Exception as e:
            self.logger.error(f"Error cargando KPIs: {e}")
            return pd.DataFrame()
    
    def get_consolidated_data(self) -> Dict:
        """
        Obtiene todos los datos consolidados del sistema.
        
        Returns:
            Diccionario consolidado con todos los datos disponibles
        """
        consolidated = {}
        
        if self.strategies_data is not None:
            consolidated['strategies'] = self.strategies_data
            
        if self.portfolio_data is not None:
            consolidated['portfolio'] = pd.DataFrame([self.portfolio_data])
            
        if self.market_data is not None:
            consolidated['market'] = self.market_data
            
        if self.kpis_data is not None:
            consolidated['kpis'] = self.kpis_data
            
        return consolidated
