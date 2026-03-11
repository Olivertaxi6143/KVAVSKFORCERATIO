#!/usr/bin/env python3
"""
MQL5Loader — Cargador de Datos de Mercado MetaTrader 4/5
=========================================================

Carga y normaliza archivos CSV exportados desde MetaTrader 4 y MetaTrader 5
(historial de barras OHLCV).

Formatos soportados:

**MetaTrader 5 — Exportación estándar:**
::

    <DATE>     <TIME>    <OPEN>    <HIGH>    <LOW>     <CLOSE>   <TICKVOL> <VOL> <SPREAD>
    2024.01.02 00:00:00 1.10234   1.10456   1.10123   1.10345   1234      0     2

**MetaTrader 4 — Historial (CSV):**
::

    2024.01.02 00:00,1.10234,1.10456,1.10123,1.10345,1234

**Formato genérico (Date, Open, High, Low, Close, Volume):**
::

    Date,Open,High,Low,Close,Volume
    2024-01-02,1.10234,1.10456,1.10123,1.10345,1234

Salida normalizada::

    datetime (DatetimeTZDtype o datetime64), open, high, low, close, volume,
    symbol, timeframe

Autor: Sistema de Análisis Cuantitativo
Fecha: 2026-03-11
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Patrones de detección de formato
# ---------------------------------------------------------------------------

# MT5: "<DATE>  <TIME>  <OPEN>  …"  (cabecera con <>)
_RE_MT5_HEADER = re.compile(r"<DATE>|<OPEN>", re.IGNORECASE)

# MT4: "2024.01.02 00:00,..." (punto como separador de fecha, espacio+hora en mismo campo)
_RE_MT4_DATETIME = re.compile(r"^\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}")

# Columnas estandarizadas de salida
_OUTPUT_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]

# Mapeos de nombres de columna para cada formato
_MT5_COL_MAP: dict[str, str] = {
    "<DATE>": "_date_raw",
    "<TIME>": "_time_raw",
    "<OPEN>": "open",
    "<HIGH>": "high",
    "<LOW>": "low",
    "<CLOSE>": "close",
    "<TICKVOL>": "volume",
    "<VOL>": "_vol_real",
    "<SPREAD>": "_spread",
    # variantes sin <>
    "DATE": "_date_raw",
    "TIME": "_time_raw",
    "OPEN": "open",
    "HIGH": "high",
    "LOW": "low",
    "CLOSE": "close",
    "TICKVOL": "volume",
    "VOL": "_vol_real",
    "SPREAD": "_spread",
}

_GENERIC_COL_MAP: dict[str, str] = {
    "Date": "_date_raw",
    "date": "_date_raw",
    "Datetime": "datetime",
    "datetime": "datetime",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "close",
    "Volume": "volume",
    "Tick Volume": "volume",
}


class MQL5Loader:
    """
    Cargador de archivos de historial OHLCV exportados desde MetaTrader 4/5.

    Detecta automáticamente el formato del archivo (MT5, MT4, genérico) y
    devuelve un DataFrame normalizado con columnas estándar.

    Args:
        symbol: Nombre del símbolo (ej. "EURUSD"). Si es None, se infiere del
                nombre del archivo.
        timeframe: Timeframe de las barras (ej. "M1", "H1"). Opcional.
    """

    def __init__(self, symbol: str | None = None, timeframe: str | None = None) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def load(self, file_path: str | Path) -> pd.DataFrame:
        """
        Carga un archivo CSV de historial de MT4/MT5 y devuelve DataFrame OHLCV.

        Args:
            file_path: Ruta al archivo CSV.

        Returns:
            DataFrame con columnas: datetime, open, high, low, close, volume,
            symbol, timeframe. Vacío si la carga falla.
        """
        path = Path(file_path)
        if not path.exists():
            self.logger.error("Archivo de mercado no encontrado: %s", path)
            return pd.DataFrame()

        try:
            formato = self._detect_format(path)
            self.logger.info("Formato detectado '%s' para: %s", formato, path.name)

            if formato == "mt5":
                df = self._load_mt5(path)
            elif formato == "mt4":
                df = self._load_mt4(path)
            else:
                df = self._load_generic(path)

            if df.empty:
                return df

            df = self._add_metadata(df, path)
            df = self._validate_ohlcv(df)

            self.logger.info(
                "Datos de mercado cargados: %d barras, símbolo=%s, timeframe=%s",
                len(df), df["symbol"].iloc[0], df["timeframe"].iloc[0],
            )
            return df

        except Exception as exc:
            self.logger.error("Error cargando datos de mercado %s: %s", path, exc)
            return pd.DataFrame()

    def load_directory(
        self, folder_path: str | Path, pattern: str = "*.csv"
    ) -> dict[str, pd.DataFrame]:
        """
        Carga todos los CSV de historial de una carpeta.

        Returns:
            Diccionario {nombre_archivo: DataFrame}.
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            self.logger.error("Directorio no encontrado: %s", folder)
            return {}

        resultado: dict[str, pd.DataFrame] = {}
        for csv_file in sorted(folder.glob(pattern)):
            df = self.load(csv_file)
            if not df.empty:
                resultado[csv_file.stem] = df

        self.logger.info(
            "Cargados %d archivos de mercado desde: %s", len(resultado), folder
        )
        return resultado

    # ------------------------------------------------------------------
    # Detección de formato
    # ------------------------------------------------------------------

    def _detect_format(self, path: Path) -> str:
        """Detecta si el CSV es MT5, MT4 o genérico leyendo las primeras líneas."""
        try:
            with open(path, encoding="utf-8-sig", errors="replace") as f:
                cabecera = f.readline()
                primera_fila = f.readline()

            if _RE_MT5_HEADER.search(cabecera):
                return "mt5"
            if _RE_MT4_DATETIME.match(primera_fila.strip()):
                return "mt4"
            return "generic"
        except Exception:
            return "generic"

    # ------------------------------------------------------------------
    # Loaders por formato
    # ------------------------------------------------------------------

    def _load_mt5(self, path: Path) -> pd.DataFrame:
        """Carga formato MT5 con cabecera <DATE> <TIME> <OPEN> …"""
        df = pd.read_csv(
            path,
            sep=r"[\t;,]+",
            engine="python",
            encoding="utf-8-sig",
        )
        # Normalizar nombres de columna (quitar <> y espacios)
        df.columns = [c.strip().strip("<>").upper() for c in df.columns]
        rename = {
            "DATE": "_date_raw",
            "TIME": "_time_raw",
            "OPEN": "open",
            "HIGH": "high",
            "LOW": "low",
            "CLOSE": "close",
            "TICKVOL": "volume",
            "VOL": "_vol_real",
            "SPREAD": "_spread",
        }
        df = df.rename(columns=rename)

        # Construir datetime
        if "_date_raw" in df.columns and "_time_raw" in df.columns:
            df["datetime"] = pd.to_datetime(
                df["_date_raw"].astype(str) + " " + df["_time_raw"].astype(str),
                format="%Y.%m.%d %H:%M:%S",
                errors="coerce",
            )
        elif "_date_raw" in df.columns:
            df["datetime"] = pd.to_datetime(
                df["_date_raw"].astype(str),
                format="%Y.%m.%d",
                errors="coerce",
            )

        return self._select_ohlcv(df)

    def _load_mt4(self, path: Path) -> pd.DataFrame:
        """Carga formato MT4: 'YYYY.MM.DD HH:MM,open,high,low,close,volume'."""
        df = pd.read_csv(
            path,
            header=None,
            names=["_datetime_raw", "open", "high", "low", "close", "volume"],
            sep=",",
            encoding="utf-8-sig",
        )
        df["datetime"] = pd.to_datetime(
            df["_datetime_raw"],
            format="%Y.%m.%d %H:%M",
            errors="coerce",
        )
        return self._select_ohlcv(df)

    def _load_generic(self, path: Path) -> pd.DataFrame:
        """Carga formato genérico con detección automática de separador."""
        for sep in (",", ";", "\t"):
            try:
                df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", low_memory=False)
                if len(df.columns) >= 5:
                    break
            except Exception:
                continue
        else:
            df = pd.read_csv(
                path, sep=None, engine="python", encoding="utf-8-sig", low_memory=False
            )

        # Normalizar columnas
        df = df.rename(columns=_GENERIC_COL_MAP)

        # Construir datetime si no existe
        if "datetime" not in df.columns and "_date_raw" in df.columns:
            df["datetime"] = pd.to_datetime(df["_date_raw"], errors="coerce")

        return self._select_ohlcv(df)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @staticmethod
    def _select_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
        """Selecciona y ordena las columnas OHLCV estándar."""
        cols_disponibles = [c for c in _OUTPUT_COLUMNS if c in df.columns]
        df = df[cols_disponibles].copy()
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "datetime" in df.columns:
            df = df.sort_values("datetime").reset_index(drop=True)
        return df

    def _add_metadata(self, df: pd.DataFrame, path: Path) -> pd.DataFrame:
        """Añade columnas de metadatos: symbol y timeframe."""
        df = df.copy()
        df["symbol"] = self.symbol or self._infer_symbol(path)
        df["timeframe"] = self.timeframe or self._infer_timeframe(path)
        return df

    @staticmethod
    def _infer_symbol(path: Path) -> str:
        """Infiere el símbolo del nombre del archivo (ej. EURUSD_M15.csv → EURUSD)."""
        stem = path.stem.upper()
        # Buscar patrón SYMBOL_TIMEFRAME o SYMBOL
        match = re.match(r"([A-Z]{3,10})", stem)
        return match.group(1) if match else stem

    @staticmethod
    def _infer_timeframe(path: Path) -> str:
        """Infiere el timeframe del nombre del archivo (ej. EURUSD_M15.csv → M15)."""
        stem = path.stem.upper()
        match = re.search(r"_(M\d+|H\d+|D\d?|W\d?|MN\d?)", stem)
        return match.group(1) if match else "UNKNOWN"

    @staticmethod
    def _validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validación básica de integridad OHLCV.
        Elimina barras con OHLC inválido o fechas nulas.
        """
        if "datetime" in df.columns:
            df = df.dropna(subset=["datetime"])
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                df = df[df[col] > 0]
        # high >= low
        if "high" in df.columns and "low" in df.columns:
            df = df[df["high"] >= df["low"]]
        return df.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Análisis básico (útil para market_regime_analyzer)
    # ------------------------------------------------------------------

    @staticmethod
    def calcular_retornos(df: pd.DataFrame) -> pd.DataFrame:
        """
        Añade columna de retornos logarítmicos al DataFrame OHLCV.

        Args:
            df: DataFrame con columna ``close``.

        Returns:
            DataFrame con columna adicional ``log_return``.
        """
        import numpy as np

        df = df.copy()
        if "close" in df.columns:
            df["log_return"] = np.log(df["close"] / df["close"].shift(1))
        return df

    @staticmethod
    def resumen(df: pd.DataFrame) -> dict[str, Any]:
        """
        Genera estadísticas básicas del historial de mercado.

        Returns:
            Diccionario con: símbolo, timeframe, barras, fecha_inicio,
            fecha_fin, precio_min, precio_max, retorno_total.
        """
        if df.empty:
            return {}
        info: dict[str, Any] = {
            "symbol": df.get("symbol", pd.Series(["UNKNOWN"])).iloc[0],
            "timeframe": df.get("timeframe", pd.Series(["UNKNOWN"])).iloc[0],
            "barras": len(df),
        }
        if "datetime" in df.columns:
            info["fecha_inicio"] = str(df["datetime"].min())
            info["fecha_fin"] = str(df["datetime"].max())
        if "close" in df.columns:
            info["precio_min"] = float(df["close"].min())
            info["precio_max"] = float(df["close"].max())
            info["retorno_total"] = float(
                (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
            )
        return info
