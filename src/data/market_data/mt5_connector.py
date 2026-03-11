#!/usr/bin/env python3
"""
MT5Connector — Conexión en Vivo con MetaTrader 5
=================================================

Módulo para obtener datos OHLCV históricos directamente desde MetaTrader 5
a través de la librería oficial ``MetaTrader5`` de Python.

La dependencia es **opcional**: si no está instalada el módulo queda disponible
pero devuelve DataFrames vacíos con advertencia.

Instalación::

    pip install MetaTrader5

Requisitos:
  - MetaTrader 5 Terminal instalado y ejecutándose en Windows
  - Cuenta activa (demo o real) en el terminal
  - La librería solo funciona en Windows (limitación de la API oficial de MT5)

Uso::

    from src.data.market_data import MT5Connector

    connector = MT5Connector()
    if connector.disponible:
        df = connector.fetch("EURUSD", "M15", bars=5000)
        df_rango = connector.fetch_range("EURUSD", "H1", "2024-01-01", "2024-12-31")
        simbolos = connector.listar_simbolos("*USD*")

Autor: Sistema de Análisis Cuantitativo
Fecha: 2026-03-11
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pandas as pd

# Importación opcional de MetaTrader5
try:
    import MetaTrader5 as mt5  # type: ignore[import-untyped]
    _MT5_DISPONIBLE = True
except ImportError:
    mt5 = None  # type: ignore[assignment]
    _MT5_DISPONIBLE = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapeo de timeframes
# ---------------------------------------------------------------------------
_TIMEFRAME_MAP: dict[str, Any] = {}

if _MT5_DISPONIBLE:
    _TIMEFRAME_MAP = {
        "M1": mt5.TIMEFRAME_M1,
        "M2": mt5.TIMEFRAME_M2,
        "M3": mt5.TIMEFRAME_M3,
        "M4": mt5.TIMEFRAME_M4,
        "M5": mt5.TIMEFRAME_M5,
        "M6": mt5.TIMEFRAME_M6,
        "M10": mt5.TIMEFRAME_M10,
        "M12": mt5.TIMEFRAME_M12,
        "M15": mt5.TIMEFRAME_M15,
        "M20": mt5.TIMEFRAME_M20,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H2": mt5.TIMEFRAME_H2,
        "H3": mt5.TIMEFRAME_H3,
        "H4": mt5.TIMEFRAME_H4,
        "H6": mt5.TIMEFRAME_H6,
        "H8": mt5.TIMEFRAME_H8,
        "H12": mt5.TIMEFRAME_H12,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
        "MN1": mt5.TIMEFRAME_MN1,
    }


class MT5Connector:
    """
    Conector en vivo con MetaTrader 5.

    Permite descargar datos históricos OHLCV directamente desde el terminal MT5
    sin necesidad de exportar archivos CSV manualmente.

    Args:
        login: Número de cuenta (opcional, usa la cuenta activa del terminal)
        server: Nombre del servidor del broker (opcional)
        password: Contraseña de la cuenta (opcional)
        timeout: Timeout de conexión en milisegundos (por defecto 60000)
    """

    def __init__(
        self,
        login: int | None = None,
        server: str | None = None,
        password: str | None = None,
        timeout: int = 60_000,
    ) -> None:
        self.login = login
        self.server = server
        self.password = password
        self.timeout = timeout
        self._conectado = False
        self.logger = logging.getLogger(__name__)

        if not _MT5_DISPONIBLE:
            self.logger.warning(
                "Librería MetaTrader5 no disponible. "
                "Instalar con: pip install MetaTrader5 (solo Windows)"
            )

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------

    @property
    def disponible(self) -> bool:
        """True si la librería MetaTrader5 está instalada."""
        return _MT5_DISPONIBLE

    @property
    def conectado(self) -> bool:
        """True si hay conexión activa con el terminal MT5."""
        return self._conectado and _MT5_DISPONIBLE

    # ------------------------------------------------------------------
    # Conexión
    # ------------------------------------------------------------------

    def conectar(self) -> bool:
        """
        Inicializa la conexión con el terminal MT5.

        Returns:
            True si la conexión fue exitosa.
        """
        if not _MT5_DISPONIBLE:
            self.logger.error("MetaTrader5 no está instalado")
            return False

        kwargs: dict[str, Any] = {"timeout": self.timeout}
        if self.login:
            kwargs["login"] = self.login
        if self.server:
            kwargs["server"] = self.server
        if self.password:
            kwargs["password"] = self.password

        if not mt5.initialize(**kwargs):
            codigo, mensaje = mt5.last_error()
            self.logger.error(
                "Error inicializando MT5 (código %d): %s", codigo, mensaje
            )
            return False

        self._conectado = True
        info = mt5.terminal_info()
        self.logger.info(
            "Conectado a MT5: %s, build=%s",
            info.name if info else "desconocido",
            info.build if info else "?",
        )
        return True

    def desconectar(self) -> None:
        """Cierra la conexión con el terminal MT5."""
        if _MT5_DISPONIBLE and self._conectado:
            mt5.shutdown()
            self._conectado = False
            self.logger.info("Desconectado de MT5")

    def __enter__(self) -> "MT5Connector":
        self.conectar()
        return self

    def __exit__(self, *_: Any) -> None:
        self.desconectar()

    # ------------------------------------------------------------------
    # Obtención de datos
    # ------------------------------------------------------------------

    def fetch(
        self,
        symbol: str,
        timeframe: str,
        bars: int = 5000,
        desde: datetime | None = None,
    ) -> pd.DataFrame:
        """
        Descarga las últimas N barras OHLCV para un símbolo y timeframe.

        Args:
            symbol: Nombre del símbolo (ej. "EURUSD", "BTCUSD")
            timeframe: Timeframe en formato SQX (ej. "M1", "H4", "D1")
            bars: Número de barras a descargar (por defecto 5000)
            desde: Fecha de inicio opcional. Si es None, toma las últimas ``bars``.

        Returns:
            DataFrame OHLCV normalizado. Vacío si falla.
        """
        if not self._verificar_conexion():
            return pd.DataFrame()

        tf = self._resolver_timeframe(timeframe)
        if tf is None:
            return pd.DataFrame()

        try:
            if desde:
                rates = mt5.copy_rates_from(symbol, tf, desde, bars)
            else:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)

            if rates is None or len(rates) == 0:
                codigo, mensaje = mt5.last_error()
                self.logger.error(
                    "Sin datos para %s %s (código %d): %s",
                    symbol, timeframe, codigo, mensaje,
                )
                return pd.DataFrame()

            df = self._rates_a_dataframe(rates, symbol, timeframe)
            self.logger.info(
                "Descargadas %d barras de %s %s", len(df), symbol, timeframe
            )
            return df

        except Exception as exc:
            self.logger.error(
                "Error descargando %s %s: %s", symbol, timeframe, exc
            )
            return pd.DataFrame()

    def fetch_range(
        self,
        symbol: str,
        timeframe: str,
        fecha_inicio: str | datetime,
        fecha_fin: str | datetime | None = None,
    ) -> pd.DataFrame:
        """
        Descarga barras OHLCV en un rango de fechas.

        Args:
            symbol: Nombre del símbolo
            timeframe: Timeframe (ej. "H1")
            fecha_inicio: Fecha de inicio (str ISO o datetime)
            fecha_fin: Fecha fin (str ISO o datetime). None = ahora.

        Returns:
            DataFrame OHLCV normalizado.
        """
        if not self._verificar_conexion():
            return pd.DataFrame()

        tf = self._resolver_timeframe(timeframe)
        if tf is None:
            return pd.DataFrame()

        dt_inicio = self._parsear_fecha(fecha_inicio)
        dt_fin = self._parsear_fecha(fecha_fin) if fecha_fin else datetime.now()

        if dt_inicio is None or dt_fin is None:
            self.logger.error("Fechas inválidas: inicio=%s, fin=%s", fecha_inicio, fecha_fin)
            return pd.DataFrame()

        try:
            rates = mt5.copy_rates_range(symbol, tf, dt_inicio, dt_fin)
            if rates is None or len(rates) == 0:
                self.logger.warning(
                    "Sin datos para %s %s en rango %s → %s",
                    symbol, timeframe, dt_inicio, dt_fin,
                )
                return pd.DataFrame()

            df = self._rates_a_dataframe(rates, symbol, timeframe)
            self.logger.info(
                "Descargadas %d barras de %s %s (%s → %s)",
                len(df), symbol, timeframe, dt_inicio.date(), dt_fin.date(),
            )
            return df

        except Exception as exc:
            self.logger.error("Error en fetch_range %s %s: %s", symbol, timeframe, exc)
            return pd.DataFrame()

    def fetch_multi(
        self,
        symbols: list[str],
        timeframe: str,
        bars: int = 5000,
    ) -> dict[str, pd.DataFrame]:
        """
        Descarga datos para múltiples símbolos en el mismo timeframe.

        Returns:
            Diccionario {symbol: DataFrame}.
        """
        resultado: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            df = self.fetch(symbol, timeframe, bars)
            if not df.empty:
                resultado[symbol] = df
        return resultado

    # ------------------------------------------------------------------
    # Información del terminal
    # ------------------------------------------------------------------

    def listar_simbolos(self, filtro: str = "") -> list[str]:
        """
        Lista los símbolos disponibles en el terminal MT5.

        Args:
            filtro: Patrón de búsqueda (ej. "*USD*", "EUR*")

        Returns:
            Lista de nombres de símbolos.
        """
        if not self._verificar_conexion():
            return []
        try:
            if filtro:
                simbolos = mt5.symbols_get(filtro)
            else:
                simbolos = mt5.symbols_get()
            return [s.name for s in simbolos] if simbolos else []
        except Exception as exc:
            self.logger.error("Error listando símbolos: %s", exc)
            return []

    def info_cuenta(self) -> dict[str, Any]:
        """
        Devuelve información de la cuenta activa del terminal.

        Returns:
            Diccionario con: balance, equity, profit, currency, leverage, server.
        """
        if not self._verificar_conexion():
            return {}
        try:
            cuenta = mt5.account_info()
            if cuenta is None:
                return {}
            return {
                "balance": cuenta.balance,
                "equity": cuenta.equity,
                "profit": cuenta.profit,
                "currency": cuenta.currency,
                "leverage": cuenta.leverage,
                "server": cuenta.server,
                "login": cuenta.login,
            }
        except Exception as exc:
            self.logger.error("Error obteniendo info de cuenta: %s", exc)
            return {}

    # ------------------------------------------------------------------
    # Utilidades privadas
    # ------------------------------------------------------------------

    def _verificar_conexion(self) -> bool:
        """Verifica disponibilidad y conexión, intentando conectar si no está."""
        if not _MT5_DISPONIBLE:
            self.logger.error("MetaTrader5 no disponible")
            return False
        if not self._conectado:
            self.logger.info("No conectado — intentando conectar automáticamente")
            return self.conectar()
        return True

    def _resolver_timeframe(self, timeframe: str) -> Any:
        """Convierte string timeframe al valor de constante MT5."""
        tf = _TIMEFRAME_MAP.get(timeframe.upper())
        if tf is None:
            self.logger.error(
                "Timeframe '%s' no soportado. Válidos: %s",
                timeframe, list(_TIMEFRAME_MAP.keys()),
            )
        return tf

    @staticmethod
    def _rates_a_dataframe(rates: Any, symbol: str, timeframe: str) -> pd.DataFrame:
        """Convierte el array numpy de MT5 a DataFrame normalizado."""
        df = pd.DataFrame(rates)
        # La columna de tiempo en MT5 es timestamp POSIX
        df["datetime"] = pd.to_datetime(df["time"], unit="s")
        df = df.rename(columns={
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "tick_volume": "volume",
        })
        df["symbol"] = symbol
        df["timeframe"] = timeframe
        cols = ["datetime", "open", "high", "low", "close", "volume", "symbol", "timeframe"]
        return df[[c for c in cols if c in df.columns]].reset_index(drop=True)

    @staticmethod
    def _parsear_fecha(fecha: str | datetime) -> datetime | None:
        """Convierte string ISO a datetime."""
        if isinstance(fecha, datetime):
            return fecha
        try:
            return pd.to_datetime(fecha).to_pydatetime()
        except Exception:
            return None
