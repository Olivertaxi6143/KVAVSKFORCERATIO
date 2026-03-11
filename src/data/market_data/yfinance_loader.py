#!/usr/bin/env python3
"""
YFinanceLoader — Datos de Mercado via yfinance
===============================================

Proveedor alternativo de datos históricos OHLCV usando la librería ``yfinance``,
que descarga datos de Yahoo Finance.

La dependencia es **opcional**: si no está instalada el módulo queda disponible
pero devuelve DataFrames vacíos con advertencia.

Instalación::

    pip install yfinance

Casos de uso:
  - Validar estrategias con datos independientes del proveedor (MT5/MQL5)
  - Descargar datos de índices bursátiles, ETFs, acciones, criptomonedas
  - Entorno de desarrollo sin acceso a MetaTrader 5

Limitaciones:
  - Solo datos de cierre ajustado (no tick data)
  - Intradiario limitado a los últimos 60 días (intervalos 1m–1h)
  - Calidad variable según el símbolo

Uso::

    from src.data.market_data import YFinanceLoader

    loader = YFinanceLoader()

    # Datos diarios de los últimos 2 años
    df = loader.fetch("AAPL", period="2y", interval="1d")

    # Datos con rango de fechas
    df = loader.fetch_range("EURUSD=X", "2023-01-01", "2024-01-01")

    # Múltiples símbolos
    dfs = loader.fetch_multi(["SPY", "QQQ", "IWM"], period="1y")

    # Equivalentes Forex para MQL5 (Yahoo Finance usa sufijo =X)
    df_eur = loader.fetch("EURUSD=X", period="1y", interval="1h")
    df_oro = loader.fetch("GC=F", period="2y")  # Gold Futures

Autor: Sistema de Análisis Cuantitativo
Fecha: 2026-03-11
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pandas as pd

# Importación opcional de yfinance
try:
    import yfinance as yf  # type: ignore[import-untyped]
    _YF_DISPONIBLE = True
except ImportError:
    yf = None  # type: ignore[assignment]
    _YF_DISPONIBLE = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Períodos e intervalos válidos en yfinance
# ---------------------------------------------------------------------------
_PERIODOS_VALIDOS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
_INTERVALOS_VALIDOS = {
    "1m", "2m", "5m", "15m", "30m", "60m", "90m",
    "1h", "1d", "5d", "1wk", "1mo", "3mo",
}

# Mapeo de timeframes SQX → intervalos yfinance
_TF_SQX_A_YF: dict[str, str] = {
    "M1": "1m",
    "M5": "5m",
    "M15": "15m",
    "M30": "30m",
    "H1": "1h",
    "H4": "60m",   # yfinance no tiene H4; se puede descargar H1 y resamplear
    "D1": "1d",
    "W1": "1wk",
    "MN1": "1mo",
}


class YFinanceLoader:
    """
    Cargador de datos históricos OHLCV desde Yahoo Finance via yfinance.

    Normaliza la salida al mismo formato que ``MQL5Loader`` y ``MT5Connector``
    para intercambiabilidad en el pipeline de análisis.

    Args:
        auto_adjust: Si True, usa precios ajustados por splits/dividendos (defecto True).
        progress: Mostrar barra de progreso de descarga (defecto False).
    """

    def __init__(self, auto_adjust: bool = True, progress: bool = False) -> None:
        self.auto_adjust = auto_adjust
        self.progress = progress
        self.logger = logging.getLogger(__name__)

        if not _YF_DISPONIBLE:
            self.logger.warning(
                "yfinance no disponible. Instalar con: pip install yfinance"
            )

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------

    @property
    def disponible(self) -> bool:
        """True si yfinance está instalado."""
        return _YF_DISPONIBLE

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def fetch(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        timeframe_sqx: str | None = None,
    ) -> pd.DataFrame:
        """
        Descarga datos históricos para un símbolo.

        Args:
            symbol: Ticker de Yahoo Finance (ej. "AAPL", "EURUSD=X", "GC=F")
            period: Período de descarga (ej. "1y", "2y", "max")
            interval: Intervalo de barras (ej. "1d", "1h", "15m")
            timeframe_sqx: Timeframe en formato SQX (ej. "H1"). Si se indica,
                           sobreescribe ``interval`` con la conversión automática.

        Returns:
            DataFrame con columnas: datetime, open, high, low, close, volume,
            symbol, timeframe. Vacío si falla.
        """
        if not _YF_DISPONIBLE:
            self.logger.error("yfinance no instalado")
            return pd.DataFrame()

        if timeframe_sqx:
            interval = _TF_SQX_A_YF.get(timeframe_sqx.upper(), interval)

        if period not in _PERIODOS_VALIDOS:
            self.logger.warning("Período '%s' inválido; usando '1y'", period)
            period = "1y"
        if interval not in _INTERVALOS_VALIDOS:
            self.logger.warning("Intervalo '%s' inválido; usando '1d'", interval)
            interval = "1d"

        try:
            ticker = yf.Ticker(symbol)
            df_raw = ticker.history(
                period=period,
                interval=interval,
                auto_adjust=self.auto_adjust,
                progress=self.progress,
            )

            if df_raw.empty:
                self.logger.warning("Sin datos para símbolo '%s'", symbol)
                return pd.DataFrame()

            df = self._normalizar(df_raw, symbol, timeframe_sqx or interval)
            self.logger.info(
                "Descargadas %d barras de %s (período=%s, intervalo=%s)",
                len(df), symbol, period, interval,
            )
            return df

        except Exception as exc:
            self.logger.error("Error descargando %s: %s", symbol, exc)
            return pd.DataFrame()

    def fetch_range(
        self,
        symbol: str,
        fecha_inicio: str | datetime,
        fecha_fin: str | datetime | None = None,
        interval: str = "1d",
        timeframe_sqx: str | None = None,
    ) -> pd.DataFrame:
        """
        Descarga datos en un rango de fechas específico.

        Args:
            symbol: Ticker de Yahoo Finance
            fecha_inicio: Fecha de inicio (str ISO "YYYY-MM-DD" o datetime)
            fecha_fin: Fecha fin. None = hoy.
            interval: Intervalo de barras
            timeframe_sqx: Timeframe SQX alternativo a ``interval``

        Returns:
            DataFrame OHLCV normalizado.
        """
        if not _YF_DISPONIBLE:
            self.logger.error("yfinance no instalado")
            return pd.DataFrame()

        if timeframe_sqx:
            interval = _TF_SQX_A_YF.get(timeframe_sqx.upper(), interval)

        start = self._parsear_fecha(fecha_inicio)
        end = self._parsear_fecha(fecha_fin) if fecha_fin else None

        try:
            ticker = yf.Ticker(symbol)
            df_raw = ticker.history(
                start=start,
                end=end,
                interval=interval,
                auto_adjust=self.auto_adjust,
                progress=self.progress,
            )

            if df_raw.empty:
                self.logger.warning(
                    "Sin datos para %s en rango %s → %s", symbol, start, end
                )
                return pd.DataFrame()

            df = self._normalizar(df_raw, symbol, timeframe_sqx or interval)
            self.logger.info(
                "Descargadas %d barras de %s (%s → %s)",
                len(df), symbol, start, end or "hoy",
            )
            return df

        except Exception as exc:
            self.logger.error("Error en fetch_range %s: %s", symbol, exc)
            return pd.DataFrame()

    def fetch_multi(
        self,
        symbols: list[str],
        period: str = "1y",
        interval: str = "1d",
    ) -> dict[str, pd.DataFrame]:
        """
        Descarga datos para múltiples símbolos.

        Returns:
            Diccionario {symbol: DataFrame}.
        """
        if not _YF_DISPONIBLE:
            self.logger.error("yfinance no instalado")
            return {}

        resultado: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            df = self.fetch(symbol, period=period, interval=interval)
            if not df.empty:
                resultado[symbol] = df

        self.logger.info(
            "Descargados %d de %d símbolos solicitados",
            len(resultado), len(symbols),
        )
        return resultado

    def resamplear(
        self,
        df: pd.DataFrame,
        timeframe_destino: str,
    ) -> pd.DataFrame:
        """
        Resamplea un DataFrame OHLCV a un timeframe mayor.

        Útil para convertir barras H1 a H4 (que yfinance no ofrece directamente).

        Args:
            df: DataFrame OHLCV normalizado con columna ``datetime``.
            timeframe_destino: Regla de pandas resample (ej. "4h", "1W", "1ME").

        Returns:
            DataFrame resampleado.
        """
        if df.empty or "datetime" not in df.columns:
            return df

        df_resampled = (
            df.set_index("datetime")
            .resample(timeframe_destino)
            .agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            })
            .dropna()
            .reset_index()
        )

        # Preservar metadatos
        for col in ("symbol", "timeframe"):
            if col in df.columns:
                df_resampled[col] = df[col].iloc[0]

        df_resampled["timeframe"] = timeframe_destino
        return df_resampled

    def info_simbolo(self, symbol: str) -> dict[str, Any]:
        """
        Devuelve información básica del símbolo desde Yahoo Finance.

        Returns:
            Diccionario con: nombre, sector, industria, moneda, país, etc.
        """
        if not _YF_DISPONIBLE:
            return {}
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            return {
                "symbol": symbol,
                "nombre": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industria": info.get("industry", ""),
                "moneda": info.get("currency", ""),
                "pais": info.get("country", ""),
                "mercado": info.get("exchange", ""),
                "tipo": info.get("quoteType", ""),
            }
        except Exception as exc:
            self.logger.error("Error obteniendo info de %s: %s", symbol, exc)
            return {"symbol": symbol}

    # ------------------------------------------------------------------
    # Utilidades privadas
    # ------------------------------------------------------------------

    @staticmethod
    def _normalizar(df_raw: pd.DataFrame, symbol: str, timeframe: str) -> pd.DataFrame:
        """Normaliza el DataFrame de yfinance al formato estándar del sistema."""
        df = df_raw.copy()

        # yfinance devuelve el índice como DatetimeIndex
        df.index.name = "datetime"
        df = df.reset_index()

        # Renombrar columnas al estándar interno
        rename = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
            "Adj Close": "close",
            "Datetime": "datetime",
            "Date": "datetime",
        }
        df = df.rename(columns=rename)

        # Asegurar que datetime sea sin timezone para compatibilidad
        if "datetime" in df.columns and hasattr(df["datetime"], "dt"):
            if df["datetime"].dt.tz is not None:
                df["datetime"] = df["datetime"].dt.tz_localize(None)

        df["symbol"] = symbol
        df["timeframe"] = timeframe

        cols = ["datetime", "open", "high", "low", "close", "volume", "symbol", "timeframe"]
        return df[[c for c in cols if c in df.columns]].reset_index(drop=True)

    @staticmethod
    def _parsear_fecha(fecha: str | datetime) -> str:
        """Convierte datetime a string ISO para yfinance."""
        if isinstance(fecha, datetime):
            return fecha.strftime("%Y-%m-%d")
        return str(fecha)
